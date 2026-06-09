import enum
import uuid
from datetime import datetime, date

from sqlalchemy import String, Text, Integer, DateTime, Date, Boolean, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from common.models.base import Base
from common.utils.enums import pg_enum
from common.utils.ids import generate_policy_id, generate_policy_version_id


class PolicyType(str, enum.Enum):
    PRIVACY_NOTICE = "privacy_notice"
    ROPA = "ropa"
    DPA = "dpa"
    COOKIE_POLICY = "cookie_policy"
    DATA_RETENTION = "data_retention"
    INCIDENT_RESPONSE = "incident_response"
    AI_GOVERNANCE = "ai_governance"
    OTHER = "other"


class PolicyStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    UNDER_REVIEW = "under_review"
    ARCHIVED = "archived"


class PolicyContentFormat(str, enum.Enum):
    MARKDOWN = "markdown"
    PLAIN_TEXT = "plain_text"


class PolicyChangeType(str, enum.Enum):
    CREATED = "created"
    EDITED = "edited"
    AI_ENHANCED = "ai_enhanced"
    APPROVED = "approved"
    ARCHIVED = "archived"


class Policy(Base):
    __tablename__ = "policies"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    policy_id: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, default=generate_policy_id
    )
    tenant_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("tenants.tenant_id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    tenant_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Core fields
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    type: Mapped[PolicyType] = mapped_column(
        pg_enum(PolicyType), nullable=False, index=True
    )
    status: Mapped[PolicyStatus] = mapped_column(
        pg_enum(PolicyStatus), nullable=False, default=PolicyStatus.DRAFT, index=True
    )
    language: Mapped[str] = mapped_column(String(10), nullable=False, default="en")
    content_format: Mapped[PolicyContentFormat] = mapped_column(
        pg_enum(PolicyContentFormat), nullable=False, default=PolicyContentFormat.MARKDOWN
    )

    # Denormalised current version content for fast reads
    current_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Metadata
    tags: Mapped[list | None] = mapped_column(ARRAY(Text), nullable=True)
    is_ai_enhanced: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Links
    regulation_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("regulations.id", ondelete="SET NULL"), nullable=True, index=True
    )
    assessment_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("assessments.id", ondelete="SET NULL"), nullable=True, index=True
    )
    related_article: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Review / approval
    next_review_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_by: Mapped[str | None] = mapped_column(String(50), nullable=True)
    reviewed_by: Mapped[str | None] = mapped_column(String(50), nullable=True)
    approved_by: Mapped[str | None] = mapped_column(String(50), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class PolicyVersion(Base):
    __tablename__ = "policy_versions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    version_id: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, default=generate_policy_version_id
    )
    tenant_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("tenants.tenant_id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    tenant_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    policy_id: Mapped[str] = mapped_column(
        String(20), ForeignKey("policies.policy_id", ondelete="CASCADE"),
        nullable=False, index=True
    )

    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[PolicyStatus] = mapped_column(
        pg_enum(PolicyStatus), nullable=False, default=PolicyStatus.DRAFT
    )
    language: Mapped[str] = mapped_column(String(10), nullable=False, default="en")
    content_format: Mapped[PolicyContentFormat] = mapped_column(
        pg_enum(PolicyContentFormat), nullable=False, default=PolicyContentFormat.MARKDOWN
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_ai_enhanced: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    change_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    change_type: Mapped[PolicyChangeType] = mapped_column(
        pg_enum(PolicyChangeType), nullable=False, default=PolicyChangeType.CREATED
    )
    changed_fields: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    created_by: Mapped[str | None] = mapped_column(String(50), nullable=True)
    reviewed_by: Mapped[str | None] = mapped_column(String(50), nullable=True)
    approved_by: Mapped[str | None] = mapped_column(String(50), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
