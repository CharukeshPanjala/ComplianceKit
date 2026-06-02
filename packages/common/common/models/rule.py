import enum
import uuid
from common.utils.enums import pg_enum
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    String, Text, DateTime, ForeignKey, UniqueConstraint,
    Boolean, Integer, func
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from common.models.base import Base
from common.utils.ids import generate_rule_id, generate_rule_version_id


class Severity(enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RuleChangeType(enum.Enum):
    TEXT_UPDATE = "text_update"
    SEVERITY_CHANGE = "severity_change"
    LOGIC_CHANGE = "logic_change"
    NEW_RULE = "new_rule"
    DEPRECATED = "deprecated"


class Rule(Base):
    __tablename__ = "rules"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    rule_id: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, default=generate_rule_id
    )
    regulation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("regulations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    regulation_version_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("regulation_versions.id", ondelete="SET NULL"), nullable=True, index=True
    )
    # current_version_id is added post-creation (circular FK with rule_versions)
    current_version_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("rule_versions.id", ondelete="SET NULL", use_alter=True, name="fk_rules_current_version"),
        nullable=True,
    )
    article: Mapped[str] = mapped_column(String(100), nullable=False)           # "Article 37"
    article_number: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 37
    article_paragraph: Mapped[str | None] = mapped_column(String(50), nullable=True)  # "1(a)"
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    chapter: Mapped[str | None] = mapped_column(String(100), nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)              # full article text
    plain_english: Mapped[str | None] = mapped_column(Text, nullable=True)      # simple explanation
    severity: Mapped[Severity] = mapped_column(
        pg_enum(Severity), nullable=False, default=Severity.MEDIUM
    )
    profile_field: Mapped[str | None] = mapped_column(String(100), nullable=True)  # "has_compliance_officer"
    evaluation_logic: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    remediation_hint: Mapped[str | None] = mapped_column(Text, nullable=True)
    remediation_steps: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    remediation_resources: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    applicability_tags: Mapped[dict] = mapped_column(JSONB, nullable=False, default=list)
    applies_to_b2c: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    applies_to_b2b: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    applies_to_sizes: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    requires_special_data: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    fine_tier: Mapped[str | None] = mapped_column(String(10), nullable=True, index=True)
    is_mandatory: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    check_type: Mapped[str] = mapped_column(String(30), nullable=False, default="informational", index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    deprecated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    embedding = mapped_column(Vector(1536), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (UniqueConstraint("regulation_id", "article"),)


class RuleVersion(Base):
    __tablename__ = "rule_versions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    version_id: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, default=generate_rule_version_id
    )
    rule_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("rules.id", ondelete="CASCADE"), nullable=False, index=True
    )
    regulation_version_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("regulation_versions.id", ondelete="SET NULL"), nullable=True, index=True
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    article: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)       # snapshot of article text
    plain_english: Mapped[str | None] = mapped_column(Text, nullable=True)
    severity: Mapped[Severity | None] = mapped_column(pg_enum(Severity), nullable=True)
    evaluation_logic: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    remediation_hint: Mapped[str | None] = mapped_column(Text, nullable=True)
    fine_tier: Mapped[str | None] = mapped_column(String(10), nullable=True)
    is_mandatory: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    remediation_steps: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    change_type: Mapped[RuleChangeType | None] = mapped_column(pg_enum(RuleChangeType), nullable=True)
    change_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )