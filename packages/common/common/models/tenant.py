import enum
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Boolean, func, Enum
from sqlalchemy.orm import Mapped, mapped_column
from common.models.base import Base
from common.utils.ids import generate_tenant_id


class TenantPlan(enum.Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    tenant_id: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        default=generate_tenant_id,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    clerk_org_id: Mapped[str | None] = mapped_column(
        String(64),
        unique=True,
        nullable=True,
    )
    plan: Mapped[TenantPlan] = mapped_column(
        Enum(TenantPlan),
        default=TenantPlan.FREE,
        nullable=False,
    )
    gdpr_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    nis2_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ai_act_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )