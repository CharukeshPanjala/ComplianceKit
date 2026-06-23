import enum
import uuid
from datetime import datetime, date

from sqlalchemy import String, Text, Integer, DateTime, Date, Boolean, ForeignKey, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from common.models.base import Base
from common.utils.enums import pg_enum
from common.utils.ids import generate_breach_id


class BreachType(str, enum.Enum):
    CONFIDENTIALITY = "confidentiality"
    INTEGRITY = "integrity"
    AVAILABILITY = "availability"
    COMBINED = "combined"


class BreachSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BreachStatus(str, enum.Enum):
    DRAFT = "draft"
    UNDER_INVESTIGATION = "under_investigation"
    REPORTED_TO_DPA = "reported_to_dpa"
    REPORTED_TO_INDIVIDUALS = "reported_to_individuals"
    CLOSED = "closed"


class BreachRegulation(str, enum.Enum):
    GDPR = "gdpr"       # 72-hour notification window
    NIS2 = "nis2"       # 24-hour notification window
    BOTH = "both"


class BreachIncident(Base):
    __tablename__ = "breach_incidents"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    public_id: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, default=generate_breach_id
    )
    tenant_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("tenants.tenant_id", ondelete="CASCADE"),
        nullable=False, index=True
    )

    # Incident details
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    breach_type: Mapped[BreachType] = mapped_column(
        pg_enum(BreachType), nullable=False, default=BreachType.CONFIDENTIALITY
    )
    severity: Mapped[BreachSeverity] = mapped_column(
        pg_enum(BreachSeverity), nullable=False, default=BreachSeverity.MEDIUM, index=True
    )
    regulation: Mapped[BreachRegulation] = mapped_column(
        pg_enum(BreachRegulation), nullable=False, default=BreachRegulation.GDPR
    )

    # Timeline
    discovered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    occurred_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reported_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Scope
    affected_individual_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    data_categories_affected: Mapped[list | None] = mapped_column(ARRAY(Text), nullable=True)

    # Status
    status: Mapped[BreachStatus] = mapped_column(
        pg_enum(BreachStatus), nullable=False, default=BreachStatus.DRAFT, index=True
    )
    notification_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # DPA notification
    dpa_notified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    dpa_notification_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Individual notification
    individuals_notified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    individuals_notification_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Response
    containment_measures: Mapped[str | None] = mapped_column(Text, nullable=True)
    root_cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    remediation_steps: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_notification_draft: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Audit
    created_by: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
