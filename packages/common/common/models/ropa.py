import enum
import uuid
from datetime import datetime, date

from sqlalchemy import String, Text, DateTime, Date, Boolean, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from common.models.base import Base
from common.utils.enums import pg_enum
from common.utils.ids import generate_ropa_id


class RopaLegalBasis(str, enum.Enum):
    CONSENT = "consent"
    CONTRACT = "contract"
    LEGAL_OBLIGATION = "legal_obligation"
    VITAL_INTERESTS = "vital_interests"
    PUBLIC_TASK = "public_task"
    LEGITIMATE_INTERESTS = "legitimate_interests"


class RopaStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class RopaSource(str, enum.Enum):
    MANUAL = "manual"
    AUTO_GENERATED = "auto_generated"


class RopaDataRole(str, enum.Enum):
    CONTROLLER = "controller"
    PROCESSOR = "processor"


class TransferMechanism(str, enum.Enum):
    SCC = "scc"
    BCR = "bcr"
    ADEQUACY_DECISION = "adequacy_decision"
    DEROGATION = "derogation"
    NONE = "none"


class SpecialCategoryCondition(str, enum.Enum):
    EXPLICIT_CONSENT = "explicit_consent"       # Art. 9(2)(a)
    EMPLOYMENT_LAW = "employment_law"           # Art. 9(2)(b)
    VITAL_INTERESTS = "vital_interests"         # Art. 9(2)(c)
    NON_PROFIT = "non_profit"                   # Art. 9(2)(d)
    MADE_PUBLIC = "made_public"                 # Art. 9(2)(e)
    LEGAL_CLAIMS = "legal_claims"               # Art. 9(2)(f)
    PUBLIC_INTEREST = "public_interest"         # Art. 9(2)(g)
    HEALTH_CARE = "health_care"                 # Art. 9(2)(h)
    PUBLIC_HEALTH = "public_health"             # Art. 9(2)(i)
    RESEARCH = "research"                       # Art. 9(2)(j)


class RopaEntry(Base):
    __tablename__ = "ropa_entries"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    public_id: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, default=generate_ropa_id
    )
    tenant_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("tenants.tenant_id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    regulation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("regulations.id", ondelete="RESTRICT"),
        nullable=False, index=True
    )
    source_profile_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("company_profiles.id", ondelete="SET NULL"),
        nullable=True, index=True
    )

    # Activity metadata
    category: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    data_role: Mapped[RopaDataRole] = mapped_column(
        pg_enum(RopaDataRole), nullable=False, default=RopaDataRole.CONTROLLER
    )
    activity_name: Mapped[str] = mapped_column(Text, nullable=False)
    purpose: Mapped[str] = mapped_column(Text, nullable=False)

    # Legal basis
    legal_basis: Mapped[RopaLegalBasis] = mapped_column(
        pg_enum(RopaLegalBasis), nullable=False, index=True
    )
    legal_obligation_reference: Mapped[str | None] = mapped_column(Text, nullable=True)
    legitimate_interest_description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Data scope
    data_categories: Mapped[list | None] = mapped_column(ARRAY(Text), nullable=True)
    data_subject_categories: Mapped[list | None] = mapped_column(ARRAY(Text), nullable=True)
    has_special_category_data: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    special_category_types: Mapped[list | None] = mapped_column(ARRAY(Text), nullable=True)
    special_category_condition: Mapped[SpecialCategoryCondition | None] = mapped_column(
        pg_enum(SpecialCategoryCondition), nullable=True
    )

    # Automated decision making (Art. 22)
    has_automated_decision_making: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    automated_decision_description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Recipients and transfers
    recipient_categories: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    processing_locations: Mapped[list | None] = mapped_column(ARRAY(Text), nullable=True)
    third_party_transfers: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    transfer_mechanism: Mapped[TransferMechanism | None] = mapped_column(
        pg_enum(TransferMechanism), nullable=True
    )
    processors: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Retention and security
    retention_period: Mapped[str | None] = mapped_column(Text, nullable=True)
    security_measures: Mapped[str | None] = mapped_column(Text, nullable=True)

    # DPIA (Art. 35)
    requires_dpia: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    dpia_completed: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    # Lifecycle
    status: Mapped[RopaStatus] = mapped_column(
        pg_enum(RopaStatus), nullable=False, default=RopaStatus.DRAFT, index=True
    )
    source: Mapped[RopaSource] = mapped_column(
        pg_enum(RopaSource), nullable=False, default=RopaSource.MANUAL
    )

    # Review / approval
    last_reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    next_review_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    reviewed_by: Mapped[str | None] = mapped_column(String(50), nullable=True)
    approved_by: Mapped[str | None] = mapped_column(String(50), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Audit
    created_by: Mapped[str | None] = mapped_column(String(50), nullable=True)
    updated_by: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
