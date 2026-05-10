import enum
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, func, Enum
from sqlalchemy.orm import Mapped, mapped_column
from common.models.base import Base
from common.utils.ids import generate_user_id


class UserRole(enum.Enum):
    ADMIN = "admin"
    MEMBER = "member"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        default=generate_user_id,
    )
    tenant_id: Mapped[str] = mapped_column(
        String(20),
        ForeignKey("tenants.tenant_id"),
        nullable=False,
        index=True,
    )
    clerk_user_id: Mapped[str | None] = mapped_column(
        String(64),
        unique=True,
        nullable=True,
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        default=UserRole.MEMBER,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )