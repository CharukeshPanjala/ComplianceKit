# WHAT: Policies API router in policy-engine | CHANGE: new file | WHY: COM-175 — generate AI-drafted policies from selected gaps, list and view policies + version history

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from common.auth.clerk import verify_token, TokenClaims
from common.db.session import get_admin_session
from common.models.assessment import Gap
from common.models.company_profile import CompanyProfile
from common.models.policy import (
    Policy, PolicyVersion, PolicyType, PolicyStatus,
    PolicyContentFormat, PolicyChangeType,
)

from app.config import settings
from app.engine.policy_generator import PolicyGenerator, GapContext, ProfileContext

router = APIRouter(prefix="/api/v1/policies", tags=["policies"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class PolicyGenerateRequest(BaseModel):
    policy_type: str
    gap_ids: list[str]

    @field_validator("gap_ids")
    @classmethod
    def at_least_one_gap(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("At least one gap_id is required")
        return v


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _get_policy(session: AsyncSession, policy_id: str, tenant_id: str) -> Policy:
    result = await session.execute(
        select(Policy).where(
            Policy.policy_id == policy_id,
            Policy.tenant_id == tenant_id,
        )
    )
    policy = result.scalar_one_or_none()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy


def _serialize(p: Policy) -> dict:
    return {
        "policy_id": p.policy_id,
        "title": p.title,
        "type": p.type.value if p.type else None,
        "status": p.status.value if p.status else None,
        "language": p.language,
        "content_format": p.content_format.value if p.content_format else None,
        "current_version": p.current_version,
        "content": p.content,
        "tags": p.tags,
        "is_ai_enhanced": p.is_ai_enhanced,
        "related_article": p.related_article,
        "next_review_date": p.next_review_date,
        "created_at": p.created_at,
        "updated_at": p.updated_at,
    }


# ── POST /api/v1/policies/generate ───────────────────────────────────────────

@router.post("/generate", status_code=201)
async def generate_policy(
    body: PolicyGenerateRequest,
    claims: TokenClaims = Depends(verify_token),
    session: AsyncSession = Depends(get_admin_session),
):
    """
    Generate (or regenerate) a policy draft from one or more selected gaps.
    Each call appends a new PolicyVersion. Re-running with different gaps
    creates a new version of the same policy (one policy per type per tenant).
    """
    try:
        policy_type = PolicyType(body.policy_type)
    except ValueError:
        raise HTTPException(status_code=422, detail=f"Invalid policy_type '{body.policy_type}'")

    gap_result = await session.execute(
        select(Gap).where(
            Gap.gap_id.in_(body.gap_ids),
            Gap.tenant_id == claims.tenant_id,
        )
    )
    gaps = list(gap_result.scalars().all())
    if not gaps:
        raise HTTPException(status_code=404, detail="No matching gaps found")

    profile_result = await session.execute(
        select(CompanyProfile).where(CompanyProfile.tenant_id == claims.tenant_id)
    )
    profile = profile_result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Company profile not found. Complete onboarding first.")

    gap_contexts = [
        GapContext(
            article=g.article,
            title=g.title,
            plain_english=g.plain_english,
            remediation_hint=g.remediation_hint,
            severity=g.severity,
            regulation_name=g.regulation_name,
        )
        for g in gaps
    ]
    profile_context = ProfileContext(
        tenant_name=profile.tenant_name or "Your Company",
        industry=profile.industry.value if profile.industry else None,
        company_size=profile.company_size.value if profile.company_size else None,
        primary_jurisdiction=profile.primary_jurisdiction,
        dpo_name=profile.dpo_name,
        dpo_email=profile.dpo_email,
        legal_contact_email=profile.legal_contact_email,
    )

    generator = PolicyGenerator(settings)
    content, is_ai_enhanced = await generator.generate(policy_type, gap_contexts, profile_context)

    label = policy_type.value.replace("_", " ").title()
    source_gap_ids = [g.gap_id for g in gaps]
    first_gap = gaps[0]

    existing_result = await session.execute(
        select(Policy).where(
            Policy.tenant_id == claims.tenant_id,
            Policy.type == policy_type,
        )
    )
    policy = existing_result.scalar_one_or_none()

    if policy:
        policy.current_version += 1
        policy.content = content
        policy.is_ai_enhanced = is_ai_enhanced
        policy.regulation_id = first_gap.regulation_id
        policy.assessment_id = first_gap.assessment_id
        version_number = policy.current_version
    else:
        policy = Policy(
            tenant_id=claims.tenant_id,
            tenant_name=profile.tenant_name,
            title=label,
            type=policy_type,
            status=PolicyStatus.DRAFT,
            content_format=PolicyContentFormat.MARKDOWN,
            current_version=1,
            content=content,
            is_ai_enhanced=is_ai_enhanced,
            regulation_id=first_gap.regulation_id,
            assessment_id=first_gap.assessment_id,
            related_article=first_gap.article,
            created_by=claims.user_id,
        )
        session.add(policy)
        await session.flush()
        version_number = 1

    version = PolicyVersion(
        tenant_id=claims.tenant_id,
        tenant_name=profile.tenant_name,
        policy_id=policy.policy_id,
        version_number=version_number,
        status=policy.status,
        content_format=PolicyContentFormat.MARKDOWN,
        title=policy.title,
        content=content,
        is_ai_enhanced=is_ai_enhanced,
        change_type=PolicyChangeType.AI_ENHANCED if is_ai_enhanced else PolicyChangeType.CREATED,
        changed_fields={"source_gap_ids": source_gap_ids},
        created_by=claims.user_id,
    )
    session.add(version)
    await session.flush()
    await session.refresh(policy)
    await session.commit()

    return _serialize(policy)


# ── GET /api/v1/policies ──────────────────────────────────────────────────────

@router.get("")
async def list_policies(
    claims: TokenClaims = Depends(verify_token),
    session: AsyncSession = Depends(get_admin_session),
):
    result = await session.execute(
        select(Policy)
        .where(Policy.tenant_id == claims.tenant_id)
        .order_by(Policy.created_at)
    )
    policies = result.scalars().all()
    return {"total": len(policies), "policies": [_serialize(p) for p in policies]}


# ── GET /api/v1/policies/{policy_id} ─────────────────────────────────────────

@router.get("/{policy_id}")
async def get_policy(
    policy_id: str,
    claims: TokenClaims = Depends(verify_token),
    session: AsyncSession = Depends(get_admin_session),
):
    policy = await _get_policy(session, policy_id, claims.tenant_id)

    versions_result = await session.execute(
        select(PolicyVersion)
        .where(PolicyVersion.policy_id == policy.policy_id)
        .order_by(PolicyVersion.version_number.desc())
    )
    versions = versions_result.scalars().all()

    data = _serialize(policy)
    data["versions"] = [
        {
            "version_id": v.version_id,
            "version_number": v.version_number,
            "is_ai_enhanced": v.is_ai_enhanced,
            "change_type": v.change_type.value if v.change_type else None,
            "created_at": v.created_at,
        }
        for v in versions
    ]
    return data
