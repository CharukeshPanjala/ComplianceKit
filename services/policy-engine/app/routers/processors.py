from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

from common.auth.clerk import verify_token, TokenClaims
from common.db.session import get_admin_session
from common.models.company_profile import CompanyProfile
from common.models.processor import (
    Processor, ProcessorRisk, ProcessorSource, ProcessorStatus, ProcessorTransferMechanism,
)
from common.models.saas_tool import SaasTool

from app.engine.processor_generator import ProcessorGenerator

router = APIRouter(prefix="/api/v1/processors", tags=["processors"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class ProcessorUpdateRequest(BaseModel):
    dpa_signed: bool | None = None
    dpa_date: date | None = None
    contract_review_date: date | None = None
    status: str | None = None
    risk_level: str | None = None
    transfer_mechanism: str | None = None
    processing_locations: list[str] | None = None
    data_categories: list[str] | None = None
    notes: str | None = None
    service_description: str | None = None
    website: str | None = None


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _get_processor(session: AsyncSession, processor_id: str, tenant_id: str) -> Processor:
    result = await session.execute(
        select(Processor).where(
            Processor.public_id == processor_id,
            Processor.tenant_id == tenant_id,
        )
    )
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Processor not found")
    return p


def _serialize(p: Processor) -> dict:
    return {
        "processor_id": p.public_id,
        "name": p.name,
        "category": p.category,
        "service_description": p.service_description,
        "website": p.website,
        "data_categories": p.data_categories,
        "data_subject_categories": p.data_subject_categories,
        "processing_locations": p.processing_locations,
        "transfer_mechanism": p.transfer_mechanism.value if p.transfer_mechanism else None,
        "dpa_signed": p.dpa_signed,
        "dpa_date": p.dpa_date.isoformat() if p.dpa_date else None,
        "contract_review_date": p.contract_review_date.isoformat() if p.contract_review_date else None,
        "risk_level": p.risk_level.value if p.risk_level else None,
        "status": p.status.value if p.status else None,
        "source": p.source.value if p.source else None,
        "sub_processors": p.sub_processors,
        "notes": p.notes,
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "updated_at": p.updated_at.isoformat() if p.updated_at else None,
    }


# ── POST /api/v1/processors/generate ─────────────────────────────────────────

@router.post("/generate")
async def generate_processors(
    claims: TokenClaims = Depends(verify_token),
    session: AsyncSession = Depends(get_admin_session),
):
    """
    Auto-generate processors from the tenant's tech stack.
    Idempotent — deletes existing AUTO_GENERATED entries and regenerates.
    """
    profile_result = await session.execute(
        select(CompanyProfile).where(CompanyProfile.tenant_id == claims.tenant_id)
    )
    profile = profile_result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Company profile not found. Complete onboarding first.")

    tool_names: list[str] = profile.tech_stack or []

    tools: list[dict] = []
    if tool_names:
        tool_result = await session.execute(
            select(SaasTool).where(SaasTool.name.in_(tool_names))
        )
        known_tools = {t.name: t for t in tool_result.scalars().all()}

        for name in tool_names:
            if name in known_tools:
                t = known_tools[name]
                tools.append({"name": t.name, "category": t.category, "website_url": t.website_url})
            else:
                tools.append({"name": name, "category": "other", "website_url": None})

    profile_dict = {"gdpr_data": profile.gdpr_data or {}}
    generator = ProcessorGenerator(profile_dict, tools)
    generated = generator.generate()

    await session.execute(
        delete(Processor).where(
            Processor.tenant_id == claims.tenant_id,
            Processor.source == ProcessorSource.AUTO_GENERATED,
        )
    )

    processors = [
        Processor(
            tenant_id=claims.tenant_id,
            name=g.name,
            category=g.category,
            data_categories=g.data_categories,
            data_subject_categories=g.data_subject_categories,
            processing_locations=g.processing_locations,
            transfer_mechanism=g.transfer_mechanism,
            risk_level=g.risk_level,
            status=g.status,
            source=g.source,
            dpa_signed=g.dpa_signed,
            created_by=claims.user_id,
        )
        for g in generated
    ]

    session.add_all(processors)
    await session.flush()
    for p in processors:
        await session.refresh(p)
    await session.commit()

    return {"generated": len(processors), "processors": [_serialize(p) for p in processors]}


# ── GET /api/v1/processors ────────────────────────────────────────────────────

@router.get("")
async def list_processors(
    status: str | None = None,
    category: str | None = None,
    risk_level: str | None = None,
    claims: TokenClaims = Depends(verify_token),
    session: AsyncSession = Depends(get_admin_session),
):
    stmt = select(Processor).where(Processor.tenant_id == claims.tenant_id)
    if status:
        try:
            stmt = stmt.where(Processor.status == ProcessorStatus(status))
        except ValueError:
            raise HTTPException(status_code=422, detail=f"Invalid status '{status}'")
    if category:
        stmt = stmt.where(Processor.category == category)
    if risk_level:
        try:
            stmt = stmt.where(Processor.risk_level == ProcessorRisk(risk_level))
        except ValueError:
            raise HTTPException(status_code=422, detail=f"Invalid risk_level '{risk_level}'")

    result = await session.execute(stmt.order_by(Processor.name))
    processors = result.scalars().all()
    return {"total": len(processors), "processors": [_serialize(p) for p in processors]}


# ── PATCH /api/v1/processors/{processor_id} ──────────────────────────────────

@router.patch("/{processor_id}")
async def update_processor(
    processor_id: str,
    body: ProcessorUpdateRequest,
    claims: TokenClaims = Depends(verify_token),
    session: AsyncSession = Depends(get_admin_session),
):
    p = await _get_processor(session, processor_id, claims.tenant_id)
    updates = body.model_dump(exclude_none=True)

    enum_fields = {
        "status": ProcessorStatus,
        "risk_level": ProcessorRisk,
        "transfer_mechanism": ProcessorTransferMechanism,
    }

    for field, value in updates.items():
        if field in enum_fields:
            try:
                setattr(p, field, enum_fields[field](value))
            except ValueError:
                raise HTTPException(status_code=422, detail=f"Invalid {field} '{value}'")
        else:
            setattr(p, field, value)

    await session.commit()
    await session.refresh(p)
    return _serialize(p)


# ── DELETE /api/v1/processors/{processor_id} ─────────────────────────────────

@router.delete("/{processor_id}", status_code=204)
async def delete_processor(
    processor_id: str,
    claims: TokenClaims = Depends(verify_token),
    session: AsyncSession = Depends(get_admin_session),
):
    p = await _get_processor(session, processor_id, claims.tenant_id)
    await session.delete(p)
    await session.commit()
