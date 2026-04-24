from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from common.config import BaseServiceSettings

settings = BaseServiceSettings()

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_admin_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Plain async DB session with no RLS tenant scoping.
    Use ONLY for admin/webhook operations where no JWT is present.
    Never use this in normal API routes — use get_tenant_session instead.
    """
    async with AsyncSessionLocal() as session:
        yield session