from collections.abc import AsyncGenerator
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from common.auth.clerk import TokenClaims, verify_token
from common.db.session import AdminSessionLocal, AppUserSessionLocal


async def _provision_if_missing(claims: TokenClaims) -> None:
    from common.models.tenant import Tenant, TenantPlan
    from common.models.user import User, UserRole

    async with AdminSessionLocal() as session:
        async with session.begin():
            tenant = await session.scalar(
                select(Tenant).where(Tenant.tenant_id == claims.tenant_id)
            )
            if not tenant:
                session.add(Tenant(
                    tenant_id=claims.tenant_id,
                    name=claims.tenant_id,
                    slug=claims.tenant_id,
                    plan=TenantPlan.FREE,
                ))
                await session.flush()

            user = await session.scalar(
                select(User).where(User.user_id == claims.user_id)
            )
            if not user:
                role = UserRole.ADMIN if claims.org_role == "org:admin" else UserRole.MEMBER
                session.add(User(
                    user_id=claims.user_id,
                    tenant_id=claims.tenant_id,
                    email=None,
                    role=role,
                ))


async def get_tenant_session(
    request: Request,
    claims: TokenClaims = Depends(verify_token),
) -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency — DB session with RLS tenant context set.
    Flow:
    1. verify_token() validates JWT and extracts tenant_id
    2. Sets tenant_id and user_id on request.state for logging middleware
    3. We open a session and SET LOCAL app.current_tenant_id
    4. RLS policies automatically filter all queries to this tenant
    5. Session is cleaned up after the request
    """
    await _provision_if_missing(claims)

    # set on request.state so logging middleware picks them up
    request.state.tenant_id = claims.tenant_id
    request.state.user_id = claims.user_id
    request.state.org_role = claims.org_role

    async with AppUserSessionLocal() as session:
        async with session.begin():
            await session.execute(
                text("SELECT set_tenant_id(:tenant_id)"),
                {"tenant_id": claims.tenant_id},
            )
            yield session