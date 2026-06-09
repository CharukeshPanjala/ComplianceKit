# WHAT: ROPA API router in policy-engine | CHANGE: new file | WHY: COM-172 — expose generate + list endpoints
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from common.auth.clerk import verify_token, TokenClaims
from common.db.session import get_admin_session
from common.models.company_profile import CompanyProfile
from common.models.regulation import Regulation
from common.models.ropa import RopaEntry, RopaSource

from app.engine.ropa_generator import RopaGenerator

router = APIRouter(prefix="/api/v1/ropa", tags=["ropa"])


# ── POST /api/v1/ropa/generate ────────────────────────────────────────────────

@router.post("/generate")
async def generate_ropa(
    claims: TokenClaims = Depends(verify_token),
    session: AsyncSession = Depends(get_admin_session),
):
    """
    Auto-generate draft ROPA entries from the tenant's company profile.
    Idempotent — deletes existing AUTO_GENERATED entries and regenerates.
    Manual entries (source=MANUAL) are never touched.
    """
    # Load profile
    profile_result = await session.execute(
        select(CompanyProfile).where(CompanyProfile.tenant_id == claims.tenant_id)
    )
    profile = profile_result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Company profile not found. Complete onboarding first.")

    # Load GDPR regulation (ROPA is a GDPR Art. 30 requirement)
    reg_result = await session.execute(
        select(Regulation).where(Regulation.name == "GDPR")
    )
    regulation = reg_result.scalar_one_or_none()
    if not regulation:
        raise HTTPException(status_code=500, detail="GDPR regulation not found. Run seed first.")

    # Delete existing auto-generated entries for this tenant
    await session.execute(
        delete(RopaEntry).where(
            RopaEntry.tenant_id == claims.tenant_id,
            RopaEntry.source == RopaSource.AUTO_GENERATED,
        )
    )

    # Build profile dict for the generator
    profile_dict = {
        "data_role": profile.data_role.value if profile.data_role else "controller",
        "data_categories_processed": profile.data_categories_processed or [],
        "processing_purposes": profile.processing_purposes or [],
        "data_subject_categories": profile.data_subject_categories or [],
        "tech_stack": profile.tech_stack or [],
        "uses_cloud_services": profile.uses_cloud_services,
        "cloud_providers": profile.cloud_providers or [],
        "primary_jurisdiction": profile.primary_jurisdiction,
        "company_size": profile.company_size.value if profile.company_size else "",
        "number_of_data_subjects": profile.number_of_data_subjects.value if profile.number_of_data_subjects else "",
        "gdpr_data": profile.gdpr_data or {},
        "ai_act_data": profile.ai_act_data or {},
    }

    # Run generator
    generator = RopaGenerator(profile_dict)
    generated = generator.generate()

    # Persist entries
    entries = [
        RopaEntry(
            tenant_id=claims.tenant_id,
            regulation_id=regulation.id,
            source_profile_id=profile.id,
            activity_name=e.activity_name,
            purpose=e.purpose,
            category=e.category,
            data_role=e.data_role,
            legal_basis=e.legal_basis,
            data_categories=e.data_categories,
            data_subject_categories=e.data_subject_categories,
            has_special_category_data=e.has_special_category_data,
            special_category_types=e.special_category_types,
            special_category_condition=e.special_category_condition,
            has_automated_decision_making=e.has_automated_decision_making,
            processing_locations=e.processing_locations,
            third_party_transfers=e.third_party_transfers,
            transfer_mechanism=e.transfer_mechanism,
            processors=e.processors,
            requires_dpia=e.requires_dpia,
            security_measures=e.security_measures,
            source=RopaSource.AUTO_GENERATED,
            created_by=claims.user_id,
        )
        for e in generated
    ]

    session.add_all(entries)
    await session.flush()
    for entry in entries:
        await session.refresh(entry)
    await session.commit()

    return {
        "generated": len(entries),
        "entries": [_serialize(e) for e in entries],
    }


# ── GET /api/v1/ropa ──────────────────────────────────────────────────────────

@router.get("")
async def list_ropa(
    claims: TokenClaims = Depends(verify_token),
    session: AsyncSession = Depends(get_admin_session),
):
    """List all ROPA entries for the tenant."""
    result = await session.execute(
        select(RopaEntry)
        .where(RopaEntry.tenant_id == claims.tenant_id)
        .order_by(RopaEntry.created_at)
    )
    entries = result.scalars().all()

    return {
        "total": len(entries),
        "entries": [_serialize(e) for e in entries],
    }


# ── Serializer ────────────────────────────────────────────────────────────────

def _serialize(e: RopaEntry) -> dict:
    return {
        "ropa_id": e.public_id,
        "activity_name": e.activity_name,
        "purpose": e.purpose,
        "category": e.category,
        "data_role": e.data_role.value if e.data_role else None,
        "legal_basis": e.legal_basis.value if e.legal_basis else None,
        "legal_obligation_reference": e.legal_obligation_reference,
        "legitimate_interest_description": e.legitimate_interest_description,
        "data_categories": e.data_categories,
        "data_subject_categories": e.data_subject_categories,
        "has_special_category_data": e.has_special_category_data,
        "special_category_types": e.special_category_types,
        "special_category_condition": e.special_category_condition.value if e.special_category_condition else None,
        "has_automated_decision_making": e.has_automated_decision_making,
        "automated_decision_description": e.automated_decision_description,
        "processing_locations": e.processing_locations,
        "third_party_transfers": e.third_party_transfers,
        "transfer_mechanism": e.transfer_mechanism.value if e.transfer_mechanism else None,
        "processors": e.processors,
        "retention_period": e.retention_period,
        "security_measures": e.security_measures,
        "requires_dpia": e.requires_dpia,
        "dpia_completed": e.dpia_completed,
        "status": e.status.value if e.status else None,
        "source": e.source.value if e.source else None,
        "last_reviewed_at": e.last_reviewed_at,
        "next_review_date": e.next_review_date,
        "created_at": e.created_at,
        "updated_at": e.updated_at,
    }
