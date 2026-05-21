from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from common.config import BaseServiceSettings

settings = BaseServiceSettings()

# Superuser engine — bypasses RLS. Only for webhooks/admin use.
admin_engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
)

AdminSessionLocal = async_sessionmaker(
    admin_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# app_user engine — RLS enforced. Used for all authenticated requests.
app_user_engine = create_async_engine(
    settings.app_user_database_url or settings.database_url,  # fallback for CI
    echo=settings.debug,
    pool_pre_ping=True,
)

AppUserSessionLocal = async_sessionmaker(
    app_user_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_admin_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Superuser session — no RLS. Use ONLY for webhooks and admin operations.
    Never use this in normal API routes.
    """
    async with AdminSessionLocal() as session:
        yield session