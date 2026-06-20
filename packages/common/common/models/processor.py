import enum
import uuid
from datetime import datetime, date

from sqlalchemy import String, Text, DateTime, Date, Boolean, ForeignKey, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from common.models.base import Base
from common.utils.enums import pg_enum
from common.utils.ids import generate_processor_id


class ProcessorStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    UNDER_REVIEW = "under_review"


class ProcessorRisk(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ProcessorSource(str, enum.Enum):
    MANUAL = "manual"
    AUTO_GENERATED = "auto_generated"


class ProcessorTransferMechanism(str, enum.Enum):
    SCC = "scc"
    BCR = "bcr"
    ADEQUACY_DECISION = "adequacy_decision"
    DEROGATION = "derogation"
    NONE = "none"


class Processor(Base):
    __tablename__ = "processors"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    public_id: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, default=generate_processor_id
    )
    tenant_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("tenants.tenant_id", ondelete="CASCADE"),
        nullable=False, index=True
    )

    # Vendor identity
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    service_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Data processing details
    data_categories: Mapped[list | None] = mapped_column(ARRAY(Text), nullable=True)
    data_subject_categories: Mapped[list | None] = mapped_column(ARRAY(Text), nullable=True)
    processing_locations: Mapped[list | None] = mapped_column(ARRAY(Text), nullable=True)

    # Transfer details (only relevant for non-EEA transfers)
    transfer_mechanism: Mapped[ProcessorTransferMechanism | None] = mapped_column(
        pg_enum(ProcessorTransferMechanism), nullable=True
    )

    # DPA / contract
    dpa_signed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    dpa_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    contract_review_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Risk
    risk_level: Mapped[ProcessorRisk] = mapped_column(
        pg_enum(ProcessorRisk), nullable=False, default=ProcessorRisk.MEDIUM
    )

    # Lifecycle
    status: Mapped[ProcessorStatus] = mapped_column(
        pg_enum(ProcessorStatus), nullable=False, default=ProcessorStatus.ACTIVE, index=True
    )
    source: Mapped[ProcessorSource] = mapped_column(
        pg_enum(ProcessorSource), nullable=False, default=ProcessorSource.MANUAL
    )

    # Sub-processors and notes
    sub_processors: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Audit
    created_by: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
