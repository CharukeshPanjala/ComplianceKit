from collections.abc import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from common.auth.clerk import TokenClaims, verify_token
from common.db.session import AsyncSessionLocal


async def get_tenant_session(
    claims: TokenClaims = Depends(verify_token),
) -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency — DB session with RLS tenant context set.
    Use this in all portal routes that need DB access.

    Flow:
    1. verify_token() validates JWT and extracts tenant_id
    2. We open a session and SET LOCAL app.current_tenant_id
    3. RLS policies automatically filter all queries to this tenant
    4. Session is cleaned up after the request
    """
    async with AsyncSessionLocal() as session:
        async with session.begin():
            await session.execute(
                text("SELECT set_tenant_id(:tenant_id)"),
                {"tenant_id": claims.tenant_id},
            )
            yield session