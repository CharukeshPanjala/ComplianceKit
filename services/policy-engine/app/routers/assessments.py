"""
COM-166 — Assessments API

POST /api/v1/assessments          → trigger new assessment (returns 202 immediately)
GET  /api/v1/assessments/latest   → latest assessment per regulation for the tenant
GET  /api/v1/assessments/{id}     → get specific assessment status + score
GET  /api/v1/assessments/{id}/gaps → get gaps for a specific assessment
"""
from datetime import datetime, timezone, timedelta

from arq import create_pool
from arq.connections import RedisSettings
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from common.auth.clerk import verify_token, TokenClaims
from common.db.session import get_admin_session
from common.models.assessment import Assessment, Gap, AssessmentStatus
from common.models.regulation import Regulation
from common.models.company_profile import CompanyProfile
from app.config import settings
from app.limiter import limiter

router = APIRouter(prefix="/api/v1/assessments", tags=["assessments"])


# ── Redis connection ──────────────────────────────────────────────────────────

def _redis_settings() -> RedisSettings:
    url = settings.redis_url.replace("redis://", "")
    host, port_db = url.split(":")
    port, db = port_db.split("/") if "/" in port_db else (port_db, "0")
    return RedisSettings(host=host, port=int(port), database=int(db))


# ── Schemas ───────────────────────────────────────────────────────────────────

class RunAssessmentRequest(BaseModel):
    regulation_name: str  # GDPR | NIS2 | EU_AI_ACT

class UpdateGapRequest(BaseModel):
    resolved: bool | None = None
    notes: str | None = None
    assigned_to: str | None = None
    due_date: str | None = None  # ISO date string "2026-08-01"


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("", status_code=202)
@limiter.limit("30/minute")
async def run_assessment(
    request: Request,
    body: RunAssessmentRequest,
    claims: TokenClaims = Depends(verify_token),
    session: AsyncSession = Depends(get_admin_session),
):
    """
    Trigger a new compliance assessment for the tenant.
    Returns 202 immediately — poll GET /assessments/{id} for status.
    If assessment already running or ran < 1 hour ago, returns existing assessment.
    """
    regulation_name = body.regulation_name.upper()

    # Validate regulation exists
    reg_result = await session.execute(
        select(Regulation).where(Regulation.name == regulation_name)
    )
    regulation = reg_result.scalar_one_or_none()
    if not regulation:
        raise HTTPException(status_code=404, detail=f"Regulation '{regulation_name}' not found")

    # Load tenant profile
    profile_result = await session.execute(
        select(CompanyProfile).where(CompanyProfile.tenant_id == claims.tenant_id)
    )
    profile = profile_result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Company profile not found. Complete onboarding first.")

    if not profile.is_complete:
        raise HTTPException(status_code=422, detail="Please complete onboarding before running an assessment.")

    # ── Cooldown check — return existing if already running ───────────────────
    cooldown_result = await session.execute(
        select(Assessment)
        .where(
            Assessment.tenant_id == claims.tenant_id,
            Assessment.regulation_id == regulation.id,
            Assessment.status.in_([AssessmentStatus.PENDING, AssessmentStatus.RUNNING]),
        )
        .limit(1)
    )
    running = cooldown_result.scalar_one_or_none()
    if running:
        return {
            "assessment_id": running.assessment_id,
            "status": running.status,
            "regulation": regulation_name,
            "message": "Assessment already in progress.",
        }

    recent_result = await session.execute(
        select(Assessment)
        .where(
            Assessment.tenant_id == claims.tenant_id,
            Assessment.regulation_id == regulation.id,
            Assessment.status == AssessmentStatus.COMPLETED,
            Assessment.completed_at >= datetime.now(timezone.utc) - timedelta(hours=1),
        )
        .limit(1)
    )
    recent = recent_result.scalar_one_or_none()
    if recent:
        return {
            "assessment_id": recent.assessment_id,
            "status": recent.status,
            "regulation": regulation_name,
            "message": "Assessment ran less than 1 hour ago. Returning existing result.",
        }

    # ── Load latest regulation version ────────────────────────────────────────
    from common.models.regulation import RegulationVersion
    version_result = await session.execute(
        select(RegulationVersion)
        .where(RegulationVersion.regulation_id == regulation.id)
        .order_by(desc(RegulationVersion.created_at))
        .limit(1)
    )
    version = version_result.scalar_one_or_none()

    # ── Find previous assessment for score tracking ───────────────────────────
    prev_result = await session.execute(
        select(Assessment)
        .where(
            Assessment.tenant_id == claims.tenant_id,
            Assessment.regulation_id == regulation.id,
            Assessment.status == AssessmentStatus.COMPLETED,
        )
        .order_by(desc(Assessment.created_at))
        .limit(1)
    )
    previous = prev_result.scalar_one_or_none()

    # ── Snapshot the profile at assessment time ───────────────────────────────
    profile_snapshot = {
        "b2b_or_b2c": profile.b2b_or_b2c,
        "data_role": profile.data_role,
        "industry": profile.industry,
        "company_size": profile.company_size,
        "primary_jurisdiction": profile.primary_jurisdiction,
        "number_of_data_subjects": profile.number_of_data_subjects,
        "data_categories_processed": profile.data_categories_processed,
        "processing_purposes": profile.processing_purposes,
        "data_subject_categories": profile.data_subject_categories,
        "uses_cloud_services": profile.uses_cloud_services,
        "cloud_providers": profile.cloud_providers,
        "has_on_premise_servers": profile.has_on_premise_servers,
        "has_compliance_officer": profile.has_compliance_officer,
        "dpo_name": profile.dpo_name,
        "dpo_email": profile.dpo_email,
        "certifications": profile.certifications,
        "previous_regulatory_action": profile.previous_regulatory_action,
        "gdpr_data": profile.gdpr_data,
        "nis2_data": profile.nis2_data,
        "ai_act_data": profile.ai_act_data,
    }

    # ── Create assessment row (status=pending) ────────────────────────────────
    assessment = Assessment(
        tenant_id=claims.tenant_id,
        regulation_id=regulation.id,
        regulation_version_id=version.id if version else None,
        previous_assessment_id=previous.id if previous else None,
        status=AssessmentStatus.PENDING,
        triggered_by=claims.user_id,
        profile_snapshot=profile_snapshot,
        expires_at=datetime.now(timezone.utc) + timedelta(days=90),
    )
    session.add(assessment)
    await session.flush()
    await session.commit()
    await session.refresh(assessment)

    # ── Queue ARQ job ─────────────────────────────────────────────────────────
    redis = await create_pool(_redis_settings())
    await redis.enqueue_job("run_assessment", assessment.assessment_id)
    await redis.aclose()

    return {
        "assessment_id": assessment.assessment_id,
        "status": assessment.status,
        "regulation": regulation_name,
        "message": "Assessment queued. Poll GET /api/v1/assessments/{id} for status.",
    }

@router.get("/latest")
async def get_latest_assessments(
    claims: TokenClaims = Depends(verify_token),
    session: AsyncSession = Depends(get_admin_session),
):
    """Get the latest completed assessment for each regulation."""
    regulations = ["GDPR", "NIS2", "EU_AI_ACT"]
    results = []

    profile_result = await session.execute(
        select(CompanyProfile).where(CompanyProfile.tenant_id == claims.tenant_id)
    )
    profile = profile_result.scalar_one_or_none()

    def _applicability(reg_name: str) -> tuple[bool, str | None]:
        if reg_name == "NIS2":
            if not profile:
                return False, "Complete your company profile to determine NIS2 applicability."
            sectors = (profile.nis2_data or {}).get("sectors", [])
            if not sectors or sectors == ["not_applicable"]:
                return False, (
                    "You indicated no applicable NIS2 sectors. NIS2 only applies to "
                    "organisations operating in the 18 critical sectors listed in Annexes I and II "
                    "(energy, transport, banking, health, digital infrastructure, etc.)."
                )
            size = str(profile.company_size.value if profile.company_size else "")
            size_exempt = {"1-10", "11-50"}
            # digital_infrastructure and public_administration are size-independent
            size_independent = {"digital_infrastructure", "public_administration"}
            in_scope_sectors = [s for s in sectors if s not in size_independent]
            if in_scope_sectors and size in size_exempt:
                return False, (
                    f"Your company ({size} employees) is below the NIS2 size threshold. "
                    "For most sectors, NIS2 applies to medium and large organisations only "
                    "(50+ employees or €10M+ annual turnover). "
                    "If your company is the sole provider of a critical service in your country, "
                    "national authorities may still designate you as in-scope."
                )
            return True, None
        if reg_name == "EU_AI_ACT":
            if not profile:
                return False, "Complete your company profile to determine EU AI Act applicability."
            uses_ai = bool((profile.ai_act_data or {}).get("uses_ai"))
            if not uses_ai:
                return False, (
                    "You indicated your organisation does not develop or use AI systems. "
                    "The EU AI Act applies only to providers (who develop/sell AI) and deployers "
                    "(who use AI in their products or services). "
                    "If you start using AI tools, re-run your profile assessment."
                )
            return True, None
        return True, None

    # Batch 1: load all regulation rows in one query
    reg_result = await session.execute(
        select(Regulation).where(Regulation.name.in_(regulations))
    )
    reg_map: dict[str, Regulation] = {r.name: r for r in reg_result.scalars().all()}

    # Batch 2: latest assessment per regulation in one query (sorted desc, group in Python)
    reg_ids = [r.id for r in reg_map.values()]
    asm_result = await session.execute(
        select(Assessment)
        .where(
            Assessment.tenant_id == claims.tenant_id,
            Assessment.regulation_id.in_(reg_ids),
        )
        .order_by(desc(Assessment.created_at))
    )
    latest_map: dict = {}
    for asm in asm_result.scalars().all():
        if asm.regulation_id not in latest_map:
            latest_map[asm.regulation_id] = asm

    # Batch 3 (conditional): last-completed score for any pending/running/failed
    need_prev = [
        reg_id
        for reg_id, asm in latest_map.items()
        if asm.status in ("pending", "running", "failed")
    ]
    prev_map: dict = {}
    if need_prev:
        prev_result = await session.execute(
            select(Assessment)
            .where(
                Assessment.tenant_id == claims.tenant_id,
                Assessment.regulation_id.in_(need_prev),
                Assessment.status == AssessmentStatus.COMPLETED,
            )
            .order_by(desc(Assessment.completed_at))
        )
        for asm in prev_result.scalars().all():
            if asm.regulation_id not in prev_map:
                prev_map[asm.regulation_id] = asm

    for reg_name in regulations:
        regulation = reg_map.get(reg_name)
        if not regulation:
            continue

        assessment = latest_map.get(regulation.id)

        last_score = None
        last_risk_level = None
        last_met = None
        last_not_met = None
        last_unknown = None
        if assessment and assessment.status in ("pending", "running", "failed"):
            prev = prev_map.get(regulation.id)
            if prev:
                last_score = prev.score
                last_risk_level = prev.risk_level
                last_met = prev.met_rules
                last_not_met = prev.not_met_rules
                last_unknown = prev.unknown_rules

        applicable, not_applicable_reason = _applicability(reg_name)

        # Determine effective status
        if assessment:
            effective_status = assessment.status
        elif applicable:
            effective_status = "never_run"
        else:
            effective_status = "not_applicable"

        # If assessment exists but all gaps are not_applicable, override status
        if assessment and assessment.status == "completed" and not applicable:
            effective_status = "not_applicable"

        applicable_count = assessment.applicable_rules or 0 if assessment else 0
        unknown_count = assessment.unknown_rules or 0 if assessment else 0
        coverage_pct = (
            round((1 - unknown_count / applicable_count) * 100)
            if applicable_count > 0 else 0
        )
        insufficient_data = (
            assessment is not None
            and assessment.status == "completed"
            and assessment.score is None
        )

        results.append({
            "regulation": reg_name,
            "assessment_id": assessment.assessment_id if assessment else None,
            "score": assessment.score if assessment else None,
            "last_score": last_score,
            "risk_level": assessment.risk_level if assessment else None,
            "last_risk_level": last_risk_level,
            "met_rules": assessment.met_rules if assessment else last_met,
            "not_met_rules": assessment.not_met_rules if assessment else last_not_met,
            "unknown_rules": assessment.unknown_rules if assessment else last_unknown,
            "completed_at": assessment.completed_at if assessment else None,
            "status": effective_status,
            "not_applicable_reason": not_applicable_reason,
            "insufficient_data": insufficient_data,
            "coverage_pct": coverage_pct,
        })

    return {"assessments": results}


@router.get("/history")
async def get_assessment_history(
    regulation: str | None = Query(None),
    limit: int = Query(10, le=50),
    claims: TokenClaims = Depends(verify_token),
    session: AsyncSession = Depends(get_admin_session),
):
    """
    Score history for trend chart.
    Returns last N completed assessments per regulation.
    """
    query = (
        select(Assessment, Regulation.name.label("regulation_name"))
        .join(Regulation, Assessment.regulation_id == Regulation.id)
        .where(
            Assessment.tenant_id == claims.tenant_id,
            Assessment.status == AssessmentStatus.COMPLETED,
        )
        .order_by(desc(Assessment.completed_at))
        .limit(limit)
    )

    if regulation:
        reg_result = await session.execute(
            select(Regulation).where(Regulation.name == regulation.upper())
        )
        reg = reg_result.scalar_one_or_none()
        if not reg:
            return {"history": []}
        query = query.where(Assessment.regulation_id == reg.id)

    result = await session.execute(query)
    rows = result.all()

    return {
        "history": [
            {
                "assessment_id": row.Assessment.assessment_id,
                "regulation": row.regulation_name,
                "score": row.Assessment.score,
                "risk_level": row.Assessment.risk_level,
                "met_rules": row.Assessment.met_rules,
                "not_met_rules": row.Assessment.not_met_rules,
                "unknown_rules": row.Assessment.unknown_rules,
                "completed_at": row.Assessment.completed_at,
            }
            for row in rows
        ]
    }


@router.get("/{assessment_id}")
async def get_assessment(
    assessment_id: str,
    claims: TokenClaims = Depends(verify_token),
    session: AsyncSession = Depends(get_admin_session),
):
    """Get assessment status and score."""
    result = await session.execute(
        select(Assessment)
        .where(
            Assessment.assessment_id == assessment_id,
            Assessment.tenant_id == claims.tenant_id,
        )
    )
    assessment = result.scalar_one_or_none()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    return {
        "assessment_id": assessment.assessment_id,
        "status": assessment.status,
        "score": assessment.score,
        "risk_level": assessment.risk_level,
        "total_rules": assessment.total_rules,
        "applicable_rules": assessment.applicable_rules,
        "met_rules": assessment.met_rules,
        "partial_rules": assessment.partial_rules,
        "not_met_rules": assessment.not_met_rules,
        "unknown_rules": assessment.unknown_rules,
        "triggered_by": assessment.triggered_by,
        "completed_at": assessment.completed_at,
        "created_at": assessment.created_at,
    }


@router.get("/{assessment_id}/gaps")
async def get_gaps(
    assessment_id: str,
    status: str | None = Query(None),
    severity: str | None = Query(None),
    category: str | None = Query(None),
    remediation_priority: str | None = Query(None),
    resolved: bool | None = Query(None),
    limit: int = Query(100, le=500),
    offset: int = Query(0),
    claims: TokenClaims = Depends(verify_token),
    session: AsyncSession = Depends(get_admin_session),
):
    """
    Get gaps for an assessment with filtering.
    Excludes not_applicable gaps by default — those aren't actionable.
    """
    # Verify assessment belongs to tenant
    assessment_result = await session.execute(
        select(Assessment)
        .where(
            Assessment.assessment_id == assessment_id,
            Assessment.tenant_id == claims.tenant_id,
        )
    )
    assessment = assessment_result.scalar_one_or_none()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    # Build query
    query = (
        select(Gap)
        .where(
            Gap.assessment_id == assessment.id,
            Gap.status != "not_applicable",  # exclude non-applicable gaps
        )
        .order_by(Gap.article_number)
    )

    if status:
        query = query.where(Gap.status == status.lower())
    if severity:
        query = query.where(Gap.severity == severity.lower())
    if category:
        query = query.where(Gap.category == category.lower())
    if remediation_priority:
        query = query.where(Gap.remediation_priority == remediation_priority.lower())
    if resolved is not None:
        query = query.where(Gap.resolved == resolved)

    query = query.offset(offset).limit(limit)

    result = await session.execute(query)
    gaps = result.scalars().all()

    return {
        "assessment_id": assessment_id,
        "total": len(gaps),
        "gaps": [
            {
                "gap_id": g.gap_id,
                "article": g.article,
                "article_number": g.article_number,
                "title": g.title,
                "plain_english": g.plain_english,
                "remediation_hint": g.remediation_hint,
                "chapter": g.chapter,
                "category": g.category,
                "severity": g.severity,
                "fine_tier": g.fine_tier,
                "status": g.status,
                "score": g.score,
                "remediation_priority": g.remediation_priority,
                "remediation_steps": g.remediation_steps,
                "evidence": g.evidence,
                "assigned_to": g.assigned_to,
                "due_date": g.due_date,
                "resolved": g.resolved,
                "resolved_at": g.resolved_at,
            }
            for g in gaps
        ],
    }


@router.patch("/{assessment_id}/gaps/{gap_id}")
async def update_gap(
    assessment_id: str,
    gap_id: str,
    body: UpdateGapRequest,
    claims: TokenClaims = Depends(verify_token),
    session: AsyncSession = Depends(get_admin_session),
):
    """
    Update a gap — resolve/unresolve, add notes, assign to user, set due date.
    """
    # Verify assessment belongs to tenant
    assessment_result = await session.execute(
        select(Assessment).where(
            Assessment.assessment_id == assessment_id,
            Assessment.tenant_id == claims.tenant_id,
        )
    )
    assessment = assessment_result.scalar_one_or_none()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    # Get the gap
    gap_result = await session.execute(
        select(Gap).where(
            Gap.gap_id == gap_id,
            Gap.assessment_id == assessment.id,
        )
    )
    gap = gap_result.scalar_one_or_none()
    if not gap:
        raise HTTPException(status_code=404, detail="Gap not found")

    # Apply updates
    if body.resolved is not None:
        gap.resolved = body.resolved
        if body.resolved:
            gap.resolved_at = datetime.now(timezone.utc)
            gap.resolved_by = claims.user_id
        else:
            gap.resolved_at = None
            gap.resolved_by = None

    if body.notes is not None:
        gap.notes = body.notes

    if body.assigned_to is not None:
        gap.assigned_to = body.assigned_to

    if body.due_date is not None:
        from datetime import date
        gap.due_date = date.fromisoformat(body.due_date)

    await session.commit()
    await session.refresh(gap)

    return {
        "gap_id": gap.gap_id,
        "resolved": gap.resolved,
        "resolved_at": gap.resolved_at,
        "resolved_by": gap.resolved_by,
        "notes": gap.notes,
        "assigned_to": gap.assigned_to,
        "due_date": gap.due_date,
    }

@router.get("/{assessment_id}/stats")
async def get_assessment_stats(
    assessment_id: str,
    claims: TokenClaims = Depends(verify_token),
    session: AsyncSession = Depends(get_admin_session),
):
    """
    Gap statistics grouped by category, severity, and chapter.
    Used for gap list header and risk heat map.
    """
    from sqlalchemy import func

    # Verify ownership
    assessment_result = await session.execute(
        select(Assessment).where(
            Assessment.assessment_id == assessment_id,
            Assessment.tenant_id == claims.tenant_id,
        )
    )
    assessment = assessment_result.scalar_one_or_none()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    # By severity
    severity_result = await session.execute(
        select(Gap.severity, Gap.status, func.count(Gap.id))
        .where(
            Gap.assessment_id == assessment.id,
            Gap.status != "not_applicable",
        )
        .group_by(Gap.severity, Gap.status)
    )
    by_severity = {}
    for severity, status, count in severity_result:
        if severity not in by_severity:
            by_severity[severity] = {}
        by_severity[severity][status] = count

    # By category
    category_result = await session.execute(
        select(Gap.category, func.count(Gap.id))
        .where(
            Gap.assessment_id == assessment.id,
            Gap.status.in_(["not_met", "unknown"]),
        )
        .group_by(Gap.category)
        .order_by(func.count(Gap.id).desc())
        .limit(10)
    )
    by_category = [
        {"category": cat, "gaps": count}
        for cat, count in category_result
    ]

    # Quick wins — low effort, high impact
    # low/medium severity not_met rules that are mandatory
    quick_wins_result = await session.execute(
        select(Gap)
        .where(
            Gap.assessment_id == assessment.id,
            Gap.status == "not_met",
            Gap.severity.in_(["medium", "low"]),
            Gap.resolved.is_(False),
        )
        .order_by(Gap.article_number)
        .limit(5)
    )
    quick_wins = quick_wins_result.scalars().all()

    return {
        "assessment_id": assessment_id,
        "by_severity": by_severity,
        "by_category": by_category,
        "quick_wins": [
            {
                "gap_id": g.gap_id,
                "article": g.article,
                "category": g.category,
                "severity": g.severity,
                "remediation_hint": g.remediation_hint,
            }
            for g in quick_wins
        ],
    }

