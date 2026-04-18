import uuid
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool
from sqlalchemy import text

from common.models.tenant import Tenant, TenantPlan
from common.models.user import User, UserRole
from common.utils.ids import generate_tenant_id, generate_user_id

SUPERUSER_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/compliancekit"
APP_USER_URL = "postgresql+asyncpg://app_user:app_password@localhost:5432/compliancekit"


def pytest_configure(config):
    config.addinivalue_line("markers", "rls: RLS isolation tests")
    config.addinivalue_line("markers", "integration: requires running database")


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_app_role():
    """Create app_user role and grant permissions — skips if already set up."""
    engine = create_async_engine(SUPERUSER_URL, poolclass=NullPool)

    async with engine.connect() as conn:
        await conn.execute(text("COMMIT"))

        # Option B guard — check if app_user already has table grants
        result = await conn.execute(text("""
            SELECT 1 FROM information_schema.role_table_grants
            WHERE grantee = 'app_user'
            LIMIT 1
        """))
        already_set_up = result.fetchone() is not None

        if not already_set_up:
            await conn.execute(text("""
                DO $$
                BEGIN
                    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'app_user') THEN
                        CREATE ROLE app_user WITH LOGIN PASSWORD 'app_password';
                    END IF;
                END $$;
            """))
            await conn.execute(text("GRANT CONNECT ON DATABASE compliancekit TO app_user"))
            await conn.execute(text("GRANT USAGE ON SCHEMA public TO app_user"))
            await conn.execute(text("GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user"))
            await conn.execute(text("GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user"))
            await conn.execute(text("GRANT EXECUTE ON FUNCTION set_tenant_id(TEXT) TO app_user"))

    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def db_session():
    """Superuser session — bypasses RLS, used for seeding test data."""
    engine = create_async_engine(SUPERUSER_URL, poolclass=NullPool)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with factory() as session:
        # health check — verify superuser connection works
        await session.execute(text("SELECT 1"))
        yield session

    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def app_session():
    """App user session — RLS enforced on this connection."""
    engine = create_async_engine(APP_USER_URL, poolclass=NullPool)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with factory() as session:
        # health check — verify app_user can connect and call set_tenant_id
        await session.execute(text("SELECT set_tenant_id('health-check')"))
        yield session

    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def two_tenants(db_session):
    """Seed two tenants with one user each. Deleted after all tests finish."""
    await db_session.execute(text("SELECT set_tenant_id('bypass-rls-test')"))

    tenant_a = Tenant(
        id=uuid.uuid4(), tenant_id=generate_tenant_id(),
        name="Tenant A", slug=f"tenant-a-{uuid.uuid4().hex[:6]}",
        plan=TenantPlan.FREE,
    )
    tenant_b = Tenant(
        id=uuid.uuid4(), tenant_id=generate_tenant_id(),
        name="Tenant B", slug=f"tenant-b-{uuid.uuid4().hex[:6]}",
        plan=TenantPlan.FREE,
    )
    db_session.add(tenant_a)
    db_session.add(tenant_b)
    await db_session.flush()

    user_a = User(
        id=uuid.uuid4(), user_id=generate_user_id(),
        tenant_id=tenant_a.tenant_id,
        email=f"user-a-{uuid.uuid4().hex[:6]}@test.com",
        role=UserRole.ADMIN,
    )
    user_b = User(
        id=uuid.uuid4(), user_id=generate_user_id(),
        tenant_id=tenant_b.tenant_id,
        email=f"user-b-{uuid.uuid4().hex[:6]}@test.com",
        role=UserRole.ADMIN,
    )
    db_session.add(user_a)
    db_session.add(user_b)
    await db_session.commit()

    yield tenant_a, tenant_b, user_a, user_b

    # teardown — delete test data after all tests finish
    await db_session.execute(text("SELECT set_tenant_id('bypass-rls-test')"))
    await db_session.execute(
        text("DELETE FROM users WHERE tenant_id IN (:a, :b)"),
        {"a": tenant_a.tenant_id, "b": tenant_b.tenant_id}
    )
    await db_session.execute(
        text("DELETE FROM tenants WHERE tenant_id IN (:a, :b)"),
        {"a": tenant_a.tenant_id, "b": tenant_b.tenant_id}
    )
    await db_session.commit()