import json
from collections.abc import AsyncGenerator
from enum import Enum
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from common.config import BaseServiceSettings

settings = BaseServiceSettings()

# ── JSON serializer ───────────────────────────────────────────────────────────

def _serialize(obj: object) -> object:
    """Handle non-JSON-serializable types — enums serialize to their value."""
    if isinstance(obj, Enum):
        return obj.value
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

_json_serializer = lambda obj: json.dumps(obj, default=_serialize)

# ── Engines ───────────────────────────────────────────────────────────────────

admin_engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    json_serializer=_json_serializer,
)

AdminSessionLocal = async_sessionmaker(
    admin_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# app_user engine — RLS enforced. Used for all authenticated requests.
app_user_engine = create_async_engine(
    settings.app_user_database_url or settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    json_serializer=_json_serializer,
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