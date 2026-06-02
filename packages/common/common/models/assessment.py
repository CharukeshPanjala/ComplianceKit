import enum
import uuid
from datetime import datetime, date

from sqlalchemy import (
    String, Text, DateTime, ForeignKey, Boolean,
    Integer, Date, func
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from common.models.base import Base
from common.utils.enums import pg_enum
from common.utils.ids import generate_assessment_id, generate_gap_id


class AssessmentStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class RiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class GapStatus(str, enum.Enum):
    MET = "met"
    PARTIAL = "partial"
    NOT_MET = "not_met"
    UNKNOWN = "unknown"
    NOT_APPLICABLE = "not_applicable"


class RemediationPriority(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Assessment(Base):
    __tablename__ = "assessments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    assessment_id: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, default=generate_assessment_id
    )
    tenant_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("tenants.tenant_id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    regulation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("regulations.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    regulation_version_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("regulation_versions.id", ondelete="SET NULL"),
        nullable=True, index=True
    )
    previous_assessment_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("assessments.id", ondelete="SET NULL"),
        nullable=True
    )
    status: Mapped[AssessmentStatus] = mapped_column(
        pg_enum(AssessmentStatus), nullable=False, default=AssessmentStatus.PENDING
    )
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    risk_level: Mapped[RiskLevel | None] = mapped_column(
        pg_enum(RiskLevel), nullable=True
    )
    total_rules: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    applicable_rules: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    met_rules: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    partial_rules: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    not_met_rules: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    unknown_rules: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    profile_snapshot: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    triggered_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Gap(Base):
    __tablename__ = "gaps"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    gap_id: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, default=generate_gap_id
    )
    assessment_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    tenant_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("tenants.tenant_id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    rule_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("rules.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    regulation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("regulations.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    regulation_version_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("regulation_versions.id", ondelete="SET NULL"),
        nullable=True
    )
    # Denormalized fields for display performance
    regulation_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    article: Mapped[str | None] = mapped_column(String(100), nullable=True)
    article_number: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    chapter: Mapped[str | None] = mapped_column(String(100), nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    severity: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    fine_tier: Mapped[str | None] = mapped_column(String(10), nullable=True)
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)      
    plain_english: Mapped[str | None] = mapped_column(Text, nullable=True)    
    remediation_hint: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Assessment results
    status: Mapped[GapStatus] = mapped_column(
        pg_enum(GapStatus), nullable=False, default=GapStatus.UNKNOWN, index=True
    )
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    evidence: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    profile_field_value: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # Remediation
    remediation_priority: Mapped[RemediationPriority | None] = mapped_column(
        pg_enum(RemediationPriority), nullable=True, index=True
    )
    remediation_steps: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    remediation_resources: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    assigned_to: Mapped[str | None] = mapped_column(String(100), nullable=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    # Resolution
    resolved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )