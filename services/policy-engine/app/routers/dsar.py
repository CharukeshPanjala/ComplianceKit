from datetime import datetime, date, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from common.auth.clerk import verify_token, TokenClaims
from common.db.session import get_admin_session
from common.models.dsar import DsarRequest, DsarRequestType, DsarStatus

router = APIRouter(prefix="/api/v1/dsar", tags=["dsar"])

GDPR_DEADLINE_DAYS = 30


# ── Schemas ───────────────────────────────────────────────────────────────────

class DsarCreateRequest(BaseModel):
    request_type: str
    requester_email: str
    requester_name: str | None = None
    description: str | None = None
    received_at: datetime | None = None


class DsarUpdateRequest(BaseModel):
    status: str | None = None
    identity_verified: bool | None = None
    identity_verification_method: str | None = None
    assigned_to: str | None = None
    rejection_reason: str | None = None
    internal_notes: str | None = None
    completed_at: datetime | None = None


# ── Helpers ───────────────────────────────────────────────────────────────────

REQUEST_TYPE_LABELS = {
    "access": "Right of Access (Art. 15)",
    "rectification": "Right to Rectification (Art. 16)",
    "erasure": "Right to Erasure (Art. 17)",
    "portability": "Right to Portability (Art. 20)",
    "restriction": "Right to Restriction (Art. 18)",
    "objection": "Right to Object (Art. 21)",
    "withdraw_consent": "Withdraw Consent (Art. 7)",
}

TERMINAL_STATUSES = {DsarStatus.COMPLETED, DsarStatus.REJECTED, DsarStatus.WITHDRAWN}


def _deadline_info(dsar: DsarRequest) -> dict:
    today = date.today()
    days_remaining = (dsar.due_date - today).days
    is_overdue = days_remaining < 0 and dsar.status not in TERMINAL_STATUSES
    return {
        "days_remaining": days_remaining,
        "is_overdue": is_overdue,
    }


async def _get_dsar(session: AsyncSession, dsar_id: str, tenant_id: str) -> DsarRequest:
    result = await session.execute(
        select(DsarRequest).where(
            DsarRequest.public_id == dsar_id,
            DsarRequest.tenant_id == tenant_id,
        )
    )
    d = result.scalar_one_or_none()
    if not d:
        raise HTTPException(status_code=404, detail="DSAR request not found")
    return d


def _serialize(d: DsarRequest) -> dict:
    return {
        "dsar_id": d.public_id,
        "request_type": d.request_type.value if d.request_type else None,
        "request_type_label": REQUEST_TYPE_LABELS.get(d.request_type.value if d.request_type else "", ""),
        "description": d.description,
        # PII fields — returned to authorised tenant users only, never logged
        "requester_email": d.requester_email,
        "requester_name": d.requester_name,
        "identity_verified": d.identity_verified,
        "identity_verification_method": d.identity_verification_method,
        "status": d.status.value if d.status else None,
        "assigned_to": d.assigned_to,
        "rejection_reason": d.rejection_reason,
        "internal_notes": d.internal_notes,
        "received_at": d.received_at.isoformat() if d.received_at else None,
        "due_date": d.due_date.isoformat() if d.due_date else None,
        "completed_at": d.completed_at.isoformat() if d.completed_at else None,
        "created_at": d.created_at.isoformat() if d.created_at else None,
        "updated_at": d.updated_at.isoformat() if d.updated_at else None,
        **_deadline_info(d),
    }


# ── POST /api/v1/dsar ─────────────────────────────────────────────────────────

@router.post("", status_code=201)
async def create_dsar(
    body: DsarCreateRequest,
    claims: TokenClaims = Depends(verify_token),
    session: AsyncSession = Depends(get_admin_session),
):
    try:
        request_type = DsarRequestType(body.request_type)
    except ValueError:
        raise HTTPException(status_code=422, detail=f"Invalid request_type '{body.request_type}'")

    received_at = body.received_at or datetime.now(timezone.utc)
    if received_at.tzinfo is None:
        received_at = received_at.replace(tzinfo=timezone.utc)

    due_date = received_at.date() + timedelta(days=GDPR_DEADLINE_DAYS)

    dsar = DsarRequest(
        tenant_id=claims.tenant_id,
        request_type=request_type,
        requester_email=body.requester_email,
        requester_name=body.requester_name,
        description=body.description,
        received_at=received_at,
        due_date=due_date,
        status=DsarStatus.PENDING,
        created_by=claims.user_id,
    )
    session.add(dsar)
    await session.flush()
    await session.refresh(dsar)
    await session.commit()
    return _serialize(dsar)


# ── GET /api/v1/dsar ──────────────────────────────────────────────────────────

@router.get("")
async def list_dsars(
    status: str | None = None,
    request_type: str | None = None,
    claims: TokenClaims = Depends(verify_token),
    session: AsyncSession = Depends(get_admin_session),
):
    stmt = select(DsarRequest).where(DsarRequest.tenant_id == claims.tenant_id)
    if status:
        try:
            stmt = stmt.where(DsarRequest.status == DsarStatus(status))
        except ValueError:
            raise HTTPException(status_code=422, detail=f"Invalid status '{status}'")
    if request_type:
        try:
            stmt = stmt.where(DsarRequest.request_type == DsarRequestType(request_type))
        except ValueError:
            raise HTTPException(status_code=422, detail=f"Invalid request_type '{request_type}'")

    result = await session.execute(stmt.order_by(DsarRequest.due_date.asc()))
    dsars = result.scalars().all()
    return {"total": len(dsars), "dsars": [_serialize(d) for d in dsars]}


# ── GET /api/v1/dsar/{dsar_id} ────────────────────────────────────────────────

@router.get("/{dsar_id}")
async def get_dsar(
    dsar_id: str,
    claims: TokenClaims = Depends(verify_token),
    session: AsyncSession = Depends(get_admin_session),
):
    d = await _get_dsar(session, dsar_id, claims.tenant_id)
    return _serialize(d)


# ── PATCH /api/v1/dsar/{dsar_id} ──────────────────────────────────────────────

@router.patch("/{dsar_id}")
async def update_dsar(
    dsar_id: str,
    body: DsarUpdateRequest,
    claims: TokenClaims = Depends(verify_token),
    session: AsyncSession = Depends(get_admin_session),
):
    d = await _get_dsar(session, dsar_id, claims.tenant_id)
    updates = body.model_dump(exclude_none=True)

    if "status" in updates:
        try:
            new_status = DsarStatus(updates.pop("status"))
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid status")
        d.status = new_status
        if new_status == DsarStatus.COMPLETED and not d.completed_at:
            d.completed_at = datetime.now(timezone.utc)

    for field, value in updates.items():
        setattr(d, field, value)

    await session.commit()
    await session.refresh(d)
    return _serialize(d)


# ── DELETE /api/v1/dsar/{dsar_id} ─────────────────────────────────────────────

@router.delete("/{dsar_id}", status_code=204)
async def delete_dsar(
    dsar_id: str,
    claims: TokenClaims = Depends(verify_token),
    session: AsyncSession = Depends(get_admin_session),
):
    d = await _get_dsar(session, dsar_id, claims.tenant_id)
    await session.delete(d)
    await session.commit()
