# WHAT: Compliance report API | CHANGE: new file | WHY: COM-177 — one-click PDF/DOCX compliance report combining all regulation assessments, gap analysis and remediation roadmap for auditors and management

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from common.auth.clerk import verify_token, TokenClaims
from common.db.session import get_admin_session
from common.models.assessment import Assessment, Gap, AssessmentStatus
from common.models.regulation import Regulation
from common.models.company_profile import CompanyProfile

from app.config import settings
from app.engine.compliance_report_generator import (
    ComplianceReportGenerator,
    GapSummary,
    RegulationSummary,
    ProfileSummary,
)
from app.engine.policy_pdf_generator import render_markdown_pdf
from app.engine.policy_docx_generator import render_markdown_docx

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])

REGULATIONS = ["GDPR", "NIS2", "EU_AI_ACT"]


# ── GET /api/v1/reports/compliance ───────────────────────────────────────────

@router.get("/compliance")
async def get_compliance_report(
    format: str = Query("pdf"),
    claims: TokenClaims = Depends(verify_token),
    session: AsyncSession = Depends(get_admin_session),
):
    """
    One-click compliance report covering all three regulations: executive summary,
    regulation breakdown, gap analysis tables and remediation roadmap.
    Returns 422 if no regulation has a completed assessment yet.
    """
    if format not in ("pdf", "docx"):
        raise HTTPException(status_code=422, detail="format must be 'pdf' or 'docx'")

    profile_result = await session.execute(
        select(CompanyProfile).where(CompanyProfile.tenant_id == claims.tenant_id)
    )
    profile = profile_result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Company profile not found. Complete onboarding first.")

    regulation_summaries: list[RegulationSummary] = []
    completed_scores: list[int] = []

    for reg_name in REGULATIONS:
        reg_result = await session.execute(select(Regulation).where(Regulation.name == reg_name))
        regulation = reg_result.scalar_one_or_none()
        if not regulation:
            regulation_summaries.append(_empty_regulation_summary(reg_name))
            continue

        assessment_result = await session.execute(
            select(Assessment)
            .where(
                Assessment.tenant_id == claims.tenant_id,
                Assessment.regulation_id == regulation.id,
            )
            .order_by(desc(Assessment.created_at))
            .limit(1)
        )
        assessment = assessment_result.scalar_one_or_none()
        if not assessment:
            regulation_summaries.append(_empty_regulation_summary(reg_name))
            continue

        gaps: list[GapSummary] = []
        if assessment.status == AssessmentStatus.COMPLETED:
            gaps_result = await session.execute(
                select(Gap)
                .where(
                    Gap.assessment_id == assessment.id,
                    Gap.status != "not_applicable",
                )
                .order_by(Gap.article_number)
            )
            gaps = [
                GapSummary(
                    article=g.article,
                    title=g.title,
                    severity=g.severity,
                    status=g.status.value,
                    remediation_priority=g.remediation_priority.value if g.remediation_priority else None,
                    remediation_hint=g.remediation_hint,
                    resolved=g.resolved,
                )
                for g in gaps_result.scalars().all()
            ]
            if assessment.score is not None:
                completed_scores.append(assessment.score)

        regulation_summaries.append(
            RegulationSummary(
                regulation_name=reg_name,
                status=assessment.status.value,
                score=assessment.score,
                risk_level=assessment.risk_level.value if assessment.risk_level else None,
                applicable_rules=assessment.applicable_rules,
                met_rules=assessment.met_rules,
                partial_rules=assessment.partial_rules,
                not_met_rules=assessment.not_met_rules,
                unknown_rules=assessment.unknown_rules,
                completed_at=assessment.completed_at,
                gaps=gaps,
            )
        )

    if not completed_scores:
        raise HTTPException(status_code=422, detail="No completed assessments yet. Run an assessment first.")

    overall_score = round(sum(completed_scores) / len(completed_scores))

    profile_summary = ProfileSummary(
        tenant_name=profile.tenant_name or "Your Company",
        industry=profile.industry.value if profile.industry else None,
        company_size=profile.company_size.value if profile.company_size else None,
        b2b_or_b2c=profile.b2b_or_b2c.value if profile.b2b_or_b2c else None,
        data_role=profile.data_role.value if profile.data_role else None,
        primary_jurisdiction=profile.primary_jurisdiction,
        has_compliance_officer=profile.has_compliance_officer,
        dpo_name=profile.dpo_name,
    )

    generator = ComplianceReportGenerator(settings)
    executive_summary, _ = await generator.generate_executive_summary(
        profile_summary, regulation_summaries, overall_score
    )
    content = generator.build_report_markdown(
        profile_summary, regulation_summaries, overall_score, executive_summary
    )

    title = f"Compliance Report — {profile.tenant_name or 'Your Company'}"
    subtitle = f"Generated {date.today().strftime('%d %B %Y')}  ·  Overall Score {overall_score}%"

    if format == "docx":
        docx_bytes = render_markdown_docx(title, subtitle, content)
        return Response(
            content=docx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": "attachment; filename=compliance_report.docx"},
        )

    pdf_bytes = render_markdown_pdf(title, subtitle, content)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=compliance_report.pdf"},
    )


# ── Helpers ───────────────────────────────────────────────────────────────────

def _empty_regulation_summary(reg_name: str) -> RegulationSummary:
    return RegulationSummary(
        regulation_name=reg_name,
        status="never_run",
        score=None,
        risk_level=None,
        applicable_rules=0,
        met_rules=0,
        partial_rules=0,
        not_met_rules=0,
        unknown_rules=0,
        completed_at=None,
        gaps=[],
    )
