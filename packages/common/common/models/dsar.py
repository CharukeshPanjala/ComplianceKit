import enum
import uuid
from datetime import datetime, date

from sqlalchemy import String, Text, DateTime, Date, Boolean, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from common.models.base import Base
from common.utils.enums import pg_enum
from common.utils.ids import generate_dsar_id


class DsarRequestType(str, enum.Enum):
    ACCESS = "access"                       # Art. 15 — right of access
    RECTIFICATION = "rectification"         # Art. 16 — right to rectify
    ERASURE = "erasure"                     # Art. 17 — right to be forgotten
    PORTABILITY = "portability"             # Art. 20 — right to data portability
    RESTRICTION = "restriction"             # Art. 18 — right to restrict processing
    OBJECTION = "objection"                 # Art. 21 — right to object
    WITHDRAW_CONSENT = "withdraw_consent"   # Art. 7(3) — withdraw consent


class DsarStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    AWAITING_INFO = "awaiting_info"
    COMPLETED = "completed"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class DsarRequest(Base):
    __tablename__ = "dsar_requests"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    public_id: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, default=generate_dsar_id
    )
    tenant_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("tenants.tenant_id", ondelete="CASCADE"),
        nullable=False, index=True
    )

    # Request details
    request_type: Mapped[DsarRequestType] = mapped_column(
        pg_enum(DsarRequestType), nullable=False, index=True
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Requester identity (PII — never log these fields)
    requester_email: Mapped[str] = mapped_column(String(255), nullable=False)
    requester_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    identity_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    identity_verification_method: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Status and assignment
    status: Mapped[DsarStatus] = mapped_column(
        pg_enum(DsarStatus), nullable=False, default=DsarStatus.PENDING, index=True
    )
    assigned_to: Mapped[str | None] = mapped_column(String(50), nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    internal_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timeline — 30-day GDPR deadline from received_at
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Audit
    created_by: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
