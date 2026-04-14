import asyncio
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "packages" / "common"))

from common.models.tenant import Tenant, TenantPlan
from common.models.user import User, UserRole
from common.utils.ids import generate_tenant_id, generate_user_id

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/compliancekit"


async def seed():
    engine = create_async_engine(DATABASE_URL)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        # Create test tenant
        tenant = Tenant(
            id=uuid.uuid4(),
            tenant_id=generate_tenant_id(),
            name="Acme GmbH",
            slug="acme-gmbh",
            plan=TenantPlan.PRO,
        )
        session.add(tenant)
        await session.flush()

        # Create test user
        user = User(
            id=uuid.uuid4(),
            user_id=generate_user_id(),
            tenant_id=tenant.tenant_id,
            email="admin@acme-gmbh.com",
            role=UserRole.ADMIN,
        )
        session.add(user)
        await session.commit()

        print(f"Tenant created: {tenant.tenant_id} — {tenant.name}")
        print(f"User created:   {user.user_id} — {user.email}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())