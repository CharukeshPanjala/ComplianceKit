# WHAT: ROPA API router in policy-engine | CHANGE: add full CRUD + PDF export | WHY: COM-173
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from common.auth.clerk import verify_token, TokenClaims
from common.db.session import get_admin_session
from common.models.company_profile import CompanyProfile
from common.models.regulation import Regulation
from common.models.ropa import (
    RopaEntry, RopaSource, RopaStatus,
    RopaLegalBasis, RopaDataRole,
    TransferMechanism, SpecialCategoryCondition,
)

from app.engine.ropa_generator import RopaGenerator
from app.engine.pdf_generator import generate_ropa_pdf

router = APIRouter(prefix="/api/v1/ropa", tags=["ropa"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class RopaCreateRequest(BaseModel):
    activity_name: str
    purpose: str
    legal_basis: str
    category: str | None = None
    data_role: str | None = None
    legal_obligation_reference: str | None = None
    legitimate_interest_description: str | None = None
    data_categories: list[str] | None = None
    data_subject_categories: list[str] | None = None
    has_special_category_data: bool = False
    special_category_types: list[str] | None = None
    special_category_condition: str | None = None
    has_automated_decision_making: bool = False
    automated_decision_description: str | None = None
    processing_locations: list[str] | None = None
    third_party_transfers: dict[str, Any] | None = None
    transfer_mechanism: str | None = None
    processors: dict[str, Any] | None = None
    retention_period: str | None = None
    security_measures: str | None = None
    requires_dpia: bool = False
    dpia_completed: bool | None = None


class RopaUpdateRequest(BaseModel):
    activity_name: str | None = None
    purpose: str | None = None
    legal_basis: str | None = None
    category: str | None = None
    data_role: str | None = None
    legal_obligation_reference: str | None = None
    legitimate_interest_description: str | None = None
    data_categories: list[str] | None = None
    data_subject_categories: list[str] | None = None
    has_special_category_data: bool | None = None
    special_category_types: list[str] | None = None
    special_category_condition: str | None = None
    has_automated_decision_making: bool | None = None
    automated_decision_description: str | None = None
    processing_locations: list[str] | None = None
    third_party_transfers: dict[str, Any] | None = None
    transfer_mechanism: str | None = None
    processors: dict[str, Any] | None = None
    retention_period: str | None = None
    security_measures: str | None = None
    requires_dpia: bool | None = None
    dpia_completed: bool | None = None


class RopaStatusRequest(BaseModel):
    status: str  # draft | active | archived


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _get_entry(session: AsyncSession, ropa_id: str, tenant_id: str) -> RopaEntry:
    result = await session.execute(
        select(RopaEntry).where(
            RopaEntry.public_id == ropa_id,
            RopaEntry.tenant_id == tenant_id,
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="ROPA entry not found")
    return entry


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
    profile_result = await session.execute(
        select(CompanyProfile).where(CompanyProfile.tenant_id == claims.tenant_id)
    )
    profile = profile_result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Company profile not found. Complete onboarding first.")

    reg_result = await session.execute(
        select(Regulation).where(Regulation.name == "GDPR")
    )
    regulation = reg_result.scalar_one_or_none()
    if not regulation:
        raise HTTPException(status_code=500, detail="GDPR regulation not found. Run seed first.")

    await session.execute(
        delete(RopaEntry).where(
            RopaEntry.tenant_id == claims.tenant_id,
            RopaEntry.source == RopaSource.AUTO_GENERATED,
        )
    )

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

    generator = RopaGenerator(profile_dict)
    generated = generator.generate()

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

    return {"generated": len(entries), "entries": [_serialize(e) for e in entries]}


# ── GET /api/v1/ropa/export/pdf ───────────────────────────────────────────────
# Must be defined BEFORE /{ropa_id} to avoid route conflict

@router.get("/export/pdf")
async def export_ropa_pdf(
    claims: TokenClaims = Depends(verify_token),
    session: AsyncSession = Depends(get_admin_session),
):
    """Download all active + draft ROPA entries as a PDF (Art. 30 register)."""
    profile_result = await session.execute(
        select(CompanyProfile).where(CompanyProfile.tenant_id == claims.tenant_id)
    )
    profile = profile_result.scalar_one_or_none()
    company_name = profile.tenant_name or "" if profile else ""

    result = await session.execute(
        select(RopaEntry)
        .where(
            RopaEntry.tenant_id == claims.tenant_id,
            RopaEntry.status != RopaStatus.ARCHIVED,
        )
        .order_by(RopaEntry.created_at)
    )
    entries = list(result.scalars().all())

    pdf_bytes = generate_ropa_pdf(entries, company_name=company_name)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=ropa-register.pdf"},
    )


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
    return {"total": len(entries), "entries": [_serialize(e) for e in entries]}


# ── POST /api/v1/ropa ─────────────────────────────────────────────────────────

@router.post("", status_code=201)
async def create_ropa(
    body: RopaCreateRequest,
    claims: TokenClaims = Depends(verify_token),
    session: AsyncSession = Depends(get_admin_session),
):
    """Create a manual ROPA entry."""
    reg_result = await session.execute(
        select(Regulation).where(Regulation.name == "GDPR")
    )
    regulation = reg_result.scalar_one_or_none()
    if not regulation:
        raise HTTPException(status_code=500, detail="GDPR regulation not found.")

    entry = RopaEntry(
        tenant_id=claims.tenant_id,
        regulation_id=regulation.id,
        source=RopaSource.MANUAL,
        created_by=claims.user_id,
        **{k: v for k, v in body.model_dump(exclude_none=True).items()
           if k not in {"legal_basis", "data_role", "transfer_mechanism", "special_category_condition"}},
    )

    if body.legal_basis:
        entry.legal_basis = RopaLegalBasis(body.legal_basis)
    if body.data_role:
        entry.data_role = RopaDataRole(body.data_role)
    if body.transfer_mechanism:
        entry.transfer_mechanism = TransferMechanism(body.transfer_mechanism)
    if body.special_category_condition:
        entry.special_category_condition = SpecialCategoryCondition(body.special_category_condition)

    session.add(entry)
    await session.flush()
    await session.refresh(entry)
    await session.commit()
    return _serialize(entry)


# ── GET /api/v1/ropa/{ropa_id} ────────────────────────────────────────────────

@router.get("/{ropa_id}")
async def get_ropa(
    ropa_id: str,
    claims: TokenClaims = Depends(verify_token),
    session: AsyncSession = Depends(get_admin_session),
):
    entry = await _get_entry(session, ropa_id, claims.tenant_id)
    return _serialize(entry)


# ── PATCH /api/v1/ropa/{ropa_id} ─────────────────────────────────────────────

@router.patch("/{ropa_id}")
async def update_ropa(
    ropa_id: str,
    body: RopaUpdateRequest,
    claims: TokenClaims = Depends(verify_token),
    session: AsyncSession = Depends(get_admin_session),
):
    """Update any field on a ROPA entry."""
    entry = await _get_entry(session, ropa_id, claims.tenant_id)

    updates = body.model_dump(exclude_none=True)
    enum_fields = {"legal_basis": RopaLegalBasis, "data_role": RopaDataRole,
                   "transfer_mechanism": TransferMechanism, "special_category_condition": SpecialCategoryCondition}

    for field, value in updates.items():
        if field in enum_fields:
            setattr(entry, field, enum_fields[field](value))
        else:
            setattr(entry, field, value)

    entry.updated_by = claims.user_id
    await session.commit()
    await session.refresh(entry)
    return _serialize(entry)


# ── PATCH /api/v1/ropa/{ropa_id}/status ──────────────────────────────────────

@router.patch("/{ropa_id}/status")
async def update_ropa_status(
    ropa_id: str,
    body: RopaStatusRequest,
    claims: TokenClaims = Depends(verify_token),
    session: AsyncSession = Depends(get_admin_session),
):
    entry = await _get_entry(session, ropa_id, claims.tenant_id)
    try:
        entry.status = RopaStatus(body.status)
    except ValueError:
        raise HTTPException(status_code=422, detail=f"Invalid status '{body.status}'. Use: draft, active, archived")
    entry.updated_by = claims.user_id
    await session.commit()
    await session.refresh(entry)
    return {"ropa_id": entry.public_id, "status": entry.status.value}


# ── DELETE /api/v1/ropa/{ropa_id} ────────────────────────────────────────────

@router.delete("/{ropa_id}", status_code=204)
async def delete_ropa(
    ropa_id: str,
    claims: TokenClaims = Depends(verify_token),
    session: AsyncSession = Depends(get_admin_session),
):
    entry = await _get_entry(session, ropa_id, claims.tenant_id)
    await session.delete(entry)
    await session.commit()


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
