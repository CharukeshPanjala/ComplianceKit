from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from svix.webhooks import Webhook, WebhookVerificationError

from common.db.session import get_admin_session
from common.models.tenant import Tenant, TenantPlan
from common.models.user import User, UserRole
from common.utils.ids import generate_tenant_id, generate_user_id
from app.config import settings

router = APIRouter()


@router.post("/clerk")
async def clerk_webhook(
    request: Request,
    db: AsyncSession = Depends(get_admin_session),
) -> dict[str, str]:
    # 1. Verify signature
    payload = await request.body()
    headers = dict(request.headers)

    try:
        wh = Webhook(settings.clerk_webhook_secret)
        event = wh.verify(payload, headers)
    except WebhookVerificationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook signature",
        )

    event_type = event.get("type")
    data = event.get("data", {})

    if event_type == "organization.created":
        await handle_org_created(data, db)
    elif event_type == "user.created":
        await handle_user_created(data, db)

    return {"status": "ok"}


async def handle_org_created(data: dict, db: AsyncSession) -> None:
    clerk_org_id: str = data["id"]
    org_name: str = data["name"]
    slug: str = data.get("slug") or org_name.lower().replace(" ", "-")

    # Duplicate guard — skip if tenant already exists for this Clerk org
    existing = await db.execute(
        select(Tenant).where(Tenant.clerk_org_id == clerk_org_id)
    )
    if existing.scalar_one_or_none():
        return

    tenant = Tenant(
        tenant_id=generate_tenant_id(),
        clerk_org_id=clerk_org_id,
        name=org_name,
        slug=slug,
        plan=TenantPlan.FREE,
    )
    db.add(tenant)
    await db.commit()


async def handle_user_created(data: dict, db: AsyncSession) -> None:
    clerk_user_id: str = data["id"]
    email: str = data.get("email_addresses", [{}])[0].get("email_address", "")

    # Get the org this user belongs to
    memberships = data.get("organization_memberships", [])
    if not memberships:
        # User has no org yet — Clerk will fire another event when they join
        return

    clerk_org_id: str = memberships[0]["organization"]["id"]

    # Find the matching tenant by stable Clerk org ID (not slug — slug can change)
    result = await db.execute(
        select(Tenant).where(Tenant.clerk_org_id == clerk_org_id)
    )
    tenant = result.scalar_one_or_none()
    if not tenant:
        # Tenant not provisioned yet — org.created webhook may not have fired
        return

    # Duplicate guard
    existing = await db.execute(
        select(User).where(User.clerk_user_id == clerk_user_id)
    )
    if existing.scalar_one_or_none():
        return

    user = User(
        user_id=generate_user_id(),
        clerk_user_id=clerk_user_id,
        tenant_id=tenant.tenant_id,
        email=email,
        role=UserRole.ADMIN,  # first user in an org is always admin
    )
    db.add(user)
    await db.commit()