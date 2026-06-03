"""
ARQ Worker — Assessment Job

Runs the full compliance assessment pipeline for a tenant asynchronously.
Pipeline:
  1. Load profile snapshot
  2. Load rules for regulation (cached)
  3. Run applicability engine
  4. Run scorer
  5. Run remediation generator
  6. Bulk save gaps to DB
  7. Update assessment status + score
"""
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from common.db.session import AdminSessionLocal
from common.models.regulation import Regulation
from common.models.rule import Rule
from common.models.assessment import Assessment, Gap, AssessmentStatus, RiskLevel, GapStatus, RemediationPriority
from app.engine.applicability import ApplicabilityEngine
from app.engine.scorer import Scorer
from app.engine.remediation import RemediationGenerator
from app.config import settings as app_settings
from arq.connections import RedisSettings as ArqRedisSettings


# ── Rule cache ────────────────────────────────────────────────────────────────
# Loaded once per worker process — rules rarely change

_rules_cache: dict[str, list[Rule]] = {}


async def _get_rules(session: AsyncSession, regulation_name: str) -> list[Rule]:
    """Load rules for a regulation — cached in memory per worker."""
    if regulation_name in _rules_cache:
        return _rules_cache[regulation_name]

    result = await session.execute(
        select(Rule)
        .join(Regulation, Rule.regulation_id == Regulation.id)
        .where(Regulation.name == regulation_name)
        .where(Rule.is_active.is_(True))
        .order_by(Rule.article_number)
    )
    rules = list(result.scalars().all())
    _rules_cache[regulation_name] = rules
    return rules


# ── ARQ Job ───────────────────────────────────────────────────────────────────

async def run_assessment(ctx: dict, assessment_id: str) -> dict:
    """
    ARQ job — runs the full assessment pipeline.
    Called by ARQ worker, triggered via API.
    """
    async with AdminSessionLocal() as session:
        # ── Load assessment ───────────────────────────────────────────────────
        result = await session.execute(
            select(Assessment).where(Assessment.assessment_id == assessment_id)
        )
        assessment = result.scalar_one_or_none()

        if not assessment:
            return {"error": f"Assessment {assessment_id} not found"}

        # Mark as running
        assessment.status = AssessmentStatus.RUNNING
        await session.flush()

        try:
            # ── Load regulation ───────────────────────────────────────────────
            reg_result = await session.execute(
                select(Regulation).where(Regulation.id == assessment.regulation_id)
            )
            regulation = reg_result.scalar_one_or_none()

            if not regulation:
                raise ValueError(f"Regulation {assessment.regulation_id} not found")

            # ── Load rules (cached) ───────────────────────────────────────────
            rules = await _get_rules(session, regulation.name)

            # ── Get profile snapshot ──────────────────────────────────────────
            profile = assessment.profile_snapshot or {}

            # ── Run applicability engine ──────────────────────────────────────
            applicability_engine = ApplicabilityEngine(
                profile=profile,
                rules=rules,
                regulation_name=regulation.name,
            )
            applicability_results = applicability_engine.evaluate()

            # ── Run scorer ────────────────────────────────────────────────────
            scorer = Scorer(
                profile=profile,
                applicability_results=applicability_results,
            )
            scoring_results = scorer.evaluate()
            score_summary = scorer.calculate_overall_score(scoring_results)

            # ── Run remediation generator ─────────────────────────────────────
            remediation_generator = RemediationGenerator(scoring_results)
            remediation_items = remediation_generator.generate()

            # ── Build gap items for not_applicable rules too ──────────────────
            # Create a map for quick lookup
            scoring_map = {r.rule.id: r for r in scoring_results}
            remediation_map = {r.rule.id: r for r in remediation_items}

            # ── Bulk create gaps ──────────────────────────────────────────────
            gaps = []
            for ar in applicability_results:
                rule = ar.rule
                scoring_result = scoring_map.get(rule.id)
                remediation_item = remediation_map.get(rule.id)

                # Determine status
                if not ar.is_applicable:
                    status = GapStatus.NOT_APPLICABLE
                    gap_score = None
                    evidence = {"reason": ar.reason}
                    priority = None
                    steps = None
                    resources = None
                elif scoring_result:
                    status = GapStatus(scoring_result.status)
                    gap_score = scoring_result.score if scoring_result.status != "unknown" else None
                    evidence = scoring_result.evidence
                    priority = RemediationPriority(remediation_item.remediation_priority) if remediation_item else None
                    steps = {"steps": remediation_item.remediation_steps} if remediation_item else None
                    resources = {"links": remediation_item.remediation_resources} if remediation_item else None
                else:
                    status = GapStatus.UNKNOWN
                    gap_score = None
                    evidence = {}
                    priority = None
                    steps = None
                    resources = None

                gap = Gap(
                    assessment_id=assessment.id,
                    tenant_id=assessment.tenant_id,
                    rule_id=rule.id,
                    regulation_id=assessment.regulation_id,
                    regulation_version_id=assessment.regulation_version_id,
                    regulation_name=regulation.name,
                    article=rule.article,
                    article_number=rule.article_number,
                    chapter=rule.chapter,
                    category=rule.category,
                    severity=rule.severity.value if rule.severity else None,
                    fine_tier=rule.fine_tier,
                    title=rule.title,
                    plain_english=rule.plain_english,
                    remediation_hint=rule.remediation_hint,
                    status=status,
                    score=gap_score,
                    evidence=evidence,
                    remediation_priority=priority,
                    remediation_steps=steps,
                    remediation_resources=resources,
                )
                gaps.append(gap)

            # Bulk insert all gaps
            session.add_all(gaps)

            # ── Update assessment ─────────────────────────────────────────────
            assessment.status = AssessmentStatus.COMPLETED
            assessment.score = score_summary["score"]
            assessment.risk_level = RiskLevel(score_summary["risk_level"])
            assessment.total_rules = len(rules)
            assessment.applicable_rules = score_summary["applicable_rules"]
            assessment.met_rules = score_summary["met_rules"]
            assessment.partial_rules = score_summary["partial_rules"]
            assessment.not_met_rules = score_summary["not_met_rules"]
            assessment.unknown_rules = score_summary["unknown_rules"]
            assessment.completed_at = datetime.now(timezone.utc)

            await session.commit()

            return {
                "assessment_id": assessment_id,
                "score": score_summary["score"],
                "risk_level": score_summary["risk_level"],
                "gaps_created": len(gaps),
            }

        except Exception as e:
            # Mark as failed
            assessment.status = AssessmentStatus.FAILED
            await session.commit()
            raise e


# ── ARQ worker settings ───────────────────────────────────────────────────────

async def startup(ctx: dict) -> None:
    """Called once when worker starts — warm up rule cache."""
    async with AdminSessionLocal() as session:
        for regulation_name in ("GDPR", "NIS2", "EU_AI_ACT"):
            await _get_rules(session, regulation_name)
    print("✅ Rule cache warmed up")


async def shutdown(ctx: dict) -> None:
    """Called when worker shuts down."""
    _rules_cache.clear()


def _parse_redis_settings() -> ArqRedisSettings:
    url = app_settings.redis_url.replace("redis://", "")
    host_port, _, db = url.partition("/")
    host, _, port = host_port.partition(":")
    return ArqRedisSettings(
        host=host or "localhost",
        port=int(port) if port else 6379,
        database=int(db) if db else 0,
    )

class WorkerSettings:
    redis_settings = _parse_redis_settings()
    functions = [run_assessment]
    on_startup = startup
    on_shutdown = shutdown
    max_jobs = 10
    job_timeout = 60