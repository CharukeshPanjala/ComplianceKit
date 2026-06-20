from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from common.auth.clerk import verify_token, TokenClaims
from common.db.session import get_admin_session
from common.models.breach import (
    BreachIncident, BreachType, BreachSeverity, BreachStatus, BreachRegulation,
)

from app.config import settings

router = APIRouter(prefix="/api/v1/breach", tags=["breach"])

# Notification windows in hours
_DEADLINE_HOURS = {
    BreachRegulation.GDPR: 72,
    BreachRegulation.NIS2: 24,
    BreachRegulation.BOTH: 24,  # tightest window
}


# ── Schemas ───────────────────────────────────────────────────────────────────

class BreachCreateRequest(BaseModel):
    title: str
    description: str | None = None
    breach_type: str = "confidentiality"
    severity: str = "medium"
    regulation: str = "gdpr"
    discovered_at: datetime
    occurred_at: datetime | None = None
    affected_individual_count: int | None = None
    data_categories_affected: list[str] | None = None
    notification_required: bool = False
    containment_measures: str | None = None
    root_cause: str | None = None
    remediation_steps: str | None = None


class BreachUpdateRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    breach_type: str | None = None
    severity: str | None = None
    regulation: str | None = None
    occurred_at: datetime | None = None
    reported_at: datetime | None = None
    affected_individual_count: int | None = None
    data_categories_affected: list[str] | None = None
    status: str | None = None
    notification_required: bool | None = None
    dpa_notified: bool | None = None
    dpa_notification_date: str | None = None
    individuals_notified: bool | None = None
    individuals_notification_date: str | None = None
    containment_measures: str | None = None
    root_cause: str | None = None
    remediation_steps: str | None = None


# ── Helpers ───────────────────────────────────────────────────────────────────

def _deadline_info(breach: BreachIncident) -> dict[str, Any]:
    hours = _DEADLINE_HOURS.get(breach.regulation, 72)
    discovered = breach.discovered_at
    if discovered.tzinfo is None:
        discovered = discovered.replace(tzinfo=timezone.utc)
    deadline = discovered.replace(tzinfo=timezone.utc) if discovered.tzinfo is None else discovered
    from datetime import timedelta
    deadline = discovered + timedelta(hours=hours)
    now = datetime.now(timezone.utc)
    remaining = (deadline - now).total_seconds() / 3600
    return {
        "deadline_hours": hours,
        "deadline_at": deadline.isoformat(),
        "hours_remaining": round(max(0.0, remaining), 1),
        "deadline_passed": remaining < 0 and not breach.dpa_notified,
    }


async def _get_breach(session: AsyncSession, breach_id: str, tenant_id: str) -> BreachIncident:
    result = await session.execute(
        select(BreachIncident).where(
            BreachIncident.public_id == breach_id,
            BreachIncident.tenant_id == tenant_id,
        )
    )
    b = result.scalar_one_or_none()
    if not b:
        raise HTTPException(status_code=404, detail="Breach incident not found")
    return b


def _serialize(b: BreachIncident) -> dict:
    return {
        "breach_id": b.public_id,
        "title": b.title,
        "description": b.description,
        "breach_type": b.breach_type.value if b.breach_type else None,
        "severity": b.severity.value if b.severity else None,
        "regulation": b.regulation.value if b.regulation else None,
        "discovered_at": b.discovered_at.isoformat() if b.discovered_at else None,
        "occurred_at": b.occurred_at.isoformat() if b.occurred_at else None,
        "reported_at": b.reported_at.isoformat() if b.reported_at else None,
        "affected_individual_count": b.affected_individual_count,
        "data_categories_affected": b.data_categories_affected,
        "status": b.status.value if b.status else None,
        "notification_required": b.notification_required,
        "dpa_notified": b.dpa_notified,
        "dpa_notification_date": b.dpa_notification_date.isoformat() if b.dpa_notification_date else None,
        "individuals_notified": b.individuals_notified,
        "individuals_notification_date": b.individuals_notification_date.isoformat() if b.individuals_notification_date else None,
        "containment_measures": b.containment_measures,
        "root_cause": b.root_cause,
        "remediation_steps": b.remediation_steps,
        "ai_notification_draft": b.ai_notification_draft,
        "created_at": b.created_at.isoformat() if b.created_at else None,
        "updated_at": b.updated_at.isoformat() if b.updated_at else None,
        **_deadline_info(b),
    }


def _draft_stub(b: BreachIncident) -> dict[str, str]:
    regulation_label = {
        BreachRegulation.GDPR: "GDPR Article 33",
        BreachRegulation.NIS2: "NIS2 Article 23",
        BreachRegulation.BOTH: "GDPR Article 33 and NIS2 Article 23",
    }.get(b.regulation, "applicable regulation")

    categories = ", ".join(b.data_categories_affected or []) or "under investigation"
    count = str(b.affected_individual_count) if b.affected_individual_count else "under investigation"
    discovered = b.discovered_at.strftime("%d %B %Y at %H:%M UTC") if b.discovered_at else "unknown"

    subject = f"Data Breach Notification — {b.title}"
    body = f"""Dear Data Protection Authority,

We are writing to notify you of a personal data breach as required under {regulation_label}.

INCIDENT SUMMARY
Title: {b.title}
Discovered: {discovered}
Breach type: {b.breach_type.value.replace("_", " ").title() if b.breach_type else "unknown"}
Severity: {b.severity.value.upper() if b.severity else "unknown"}
Affected individuals: {count}
Data categories affected: {categories}

DESCRIPTION
{b.description or "Further details are being gathered as the investigation progresses."}

CONTAINMENT MEASURES
{b.containment_measures or "Immediate containment measures are being implemented and will be reported in a follow-up notification."}

ROOT CAUSE
{b.root_cause or "Root cause analysis is ongoing."}

REMEDIATION
{b.remediation_steps or "Remediation steps are being defined and will be communicated in a follow-up notification."}

We will provide further updates as the investigation progresses. Please do not hesitate to contact us for additional information.

Yours faithfully,
[Data Protection Officer / Responsible Person]
[Organisation Name]
[Contact Details]"""

    return {"subject": subject, "body": body}


async def _draft_ai(b: BreachIncident) -> dict[str, str]:
    from common.ai.client import get_async_client
    client = get_async_client(settings)
    stub = _draft_stub(b)

    regulation_label = {
        BreachRegulation.GDPR: "GDPR Article 33",
        BreachRegulation.NIS2: "NIS2 Article 23",
        BreachRegulation.BOTH: "GDPR Article 33 and NIS2 Article 23",
    }.get(b.regulation, "applicable regulation")

    prompt = f"""You are a GDPR/NIS2 compliance expert. Draft a formal data breach notification letter to the Data Protection Authority.

Incident details:
- Title: {b.title}
- Description: {b.description or "Not provided"}
- Breach type: {b.breach_type.value if b.breach_type else "unknown"}
- Severity: {b.severity.value if b.severity else "unknown"}
- Regulation: {regulation_label}
- Discovered: {b.discovered_at.isoformat() if b.discovered_at else "unknown"}
- Affected individuals: {b.affected_individual_count or "under investigation"}
- Data categories: {", ".join(b.data_categories_affected or []) or "under investigation"}
- Containment: {b.containment_measures or "ongoing"}
- Root cause: {b.root_cause or "under investigation"}

Write a professional notification letter. Use formal language. Include all legally required elements under {regulation_label}.
Return ONLY the letter body text, no preamble."""

    try:
        resp = await client.chat.completions.create(
            model=settings.azure_openai_deployment,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1200,
        )
        body = resp.choices[0].message.content or stub["body"]
        return {"subject": stub["subject"], "body": body}
    except Exception:
        return stub


# ── POST /api/v1/breach ───────────────────────────────────────────────────────

@router.post("", status_code=201)
async def create_breach(
    body: BreachCreateRequest,
    claims: TokenClaims = Depends(verify_token),
    session: AsyncSession = Depends(get_admin_session),
):
    enum_map = {
        "breach_type": (BreachType, body.breach_type),
        "severity": (BreachSeverity, body.severity),
        "regulation": (BreachRegulation, body.regulation),
    }
    parsed: dict[str, Any] = {}
    for field, (enum_cls, value) in enum_map.items():
        try:
            parsed[field] = enum_cls(value)
        except ValueError:
            raise HTTPException(status_code=422, detail=f"Invalid {field} '{value}'")

    breach = BreachIncident(
        tenant_id=claims.tenant_id,
        title=body.title,
        description=body.description,
        breach_type=parsed["breach_type"],
        severity=parsed["severity"],
        regulation=parsed["regulation"],
        discovered_at=body.discovered_at,
        occurred_at=body.occurred_at,
        affected_individual_count=body.affected_individual_count,
        data_categories_affected=body.data_categories_affected,
        notification_required=body.notification_required,
        containment_measures=body.containment_measures,
        root_cause=body.root_cause,
        remediation_steps=body.remediation_steps,
        status=BreachStatus.DRAFT,
        created_by=claims.user_id,
    )
    session.add(breach)
    await session.flush()
    await session.refresh(breach)
    await session.commit()
    return _serialize(breach)


# ── GET /api/v1/breach ────────────────────────────────────────────────────────

@router.get("")
async def list_breaches(
    status: str | None = None,
    severity: str | None = None,
    regulation: str | None = None,
    claims: TokenClaims = Depends(verify_token),
    session: AsyncSession = Depends(get_admin_session),
):
    stmt = select(BreachIncident).where(BreachIncident.tenant_id == claims.tenant_id)
    if status:
        try:
            stmt = stmt.where(BreachIncident.status == BreachStatus(status))
        except ValueError:
            raise HTTPException(status_code=422, detail=f"Invalid status '{status}'")
    if severity:
        try:
            stmt = stmt.where(BreachIncident.severity == BreachSeverity(severity))
        except ValueError:
            raise HTTPException(status_code=422, detail=f"Invalid severity '{severity}'")
    if regulation:
        try:
            stmt = stmt.where(BreachIncident.regulation == BreachRegulation(regulation))
        except ValueError:
            raise HTTPException(status_code=422, detail=f"Invalid regulation '{regulation}'")

    result = await session.execute(stmt.order_by(BreachIncident.discovered_at.desc()))
    breaches = result.scalars().all()
    return {"total": len(breaches), "breaches": [_serialize(b) for b in breaches]}


# ── GET /api/v1/breach/{breach_id} ────────────────────────────────────────────

@router.get("/{breach_id}")
async def get_breach(
    breach_id: str,
    claims: TokenClaims = Depends(verify_token),
    session: AsyncSession = Depends(get_admin_session),
):
    b = await _get_breach(session, breach_id, claims.tenant_id)
    return _serialize(b)


# ── PATCH /api/v1/breach/{breach_id} ─────────────────────────────────────────

@router.patch("/{breach_id}")
async def update_breach(
    breach_id: str,
    body: BreachUpdateRequest,
    claims: TokenClaims = Depends(verify_token),
    session: AsyncSession = Depends(get_admin_session),
):
    b = await _get_breach(session, breach_id, claims.tenant_id)
    updates = body.model_dump(exclude_none=True)

    enum_fields = {
        "breach_type": BreachType,
        "severity": BreachSeverity,
        "regulation": BreachRegulation,
        "status": BreachStatus,
    }
    date_fields = {"dpa_notification_date", "individuals_notification_date"}

    for field, value in updates.items():
        if field in enum_fields:
            try:
                setattr(b, field, enum_fields[field](value))
            except ValueError:
                raise HTTPException(status_code=422, detail=f"Invalid {field} '{value}'")
        elif field in date_fields:
            from datetime import date as _date
            setattr(b, field, _date.fromisoformat(value) if value else None)
        else:
            setattr(b, field, value)

    await session.commit()
    await session.refresh(b)
    return _serialize(b)


# ── DELETE /api/v1/breach/{breach_id} ────────────────────────────────────────

@router.delete("/{breach_id}", status_code=204)
async def delete_breach(
    breach_id: str,
    claims: TokenClaims = Depends(verify_token),
    session: AsyncSession = Depends(get_admin_session),
):
    b = await _get_breach(session, breach_id, claims.tenant_id)
    await session.delete(b)
    await session.commit()


# ── POST /api/v1/breach/{breach_id}/draft-notification ───────────────────────

@router.post("/{breach_id}/draft-notification")
async def draft_notification(
    breach_id: str,
    claims: TokenClaims = Depends(verify_token),
    session: AsyncSession = Depends(get_admin_session),
):
    b = await _get_breach(session, breach_id, claims.tenant_id)

    if settings.ai_enabled:
        draft = await _draft_ai(b)
    else:
        draft = _draft_stub(b)

    b.ai_notification_draft = draft
    await session.commit()
    await session.refresh(b)
    return {"breach_id": b.public_id, "draft": draft}
