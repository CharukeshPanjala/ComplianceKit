import enum
import uuid
from common.utils.enums import pg_enum
from datetime import datetime, date

from sqlalchemy import String, Date, Text, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from common.models.base import Base
from common.utils.ids import generate_regulation_id, generate_regulation_version_id


class RegulationStatus(enum.Enum):
    ACTIVE = "active"
    COMING_SOON = "coming_soon"
    DEPRECATED = "deprecated"


class ImpactLevel(enum.Enum):
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"


class DetectedBy(enum.Enum):
    MANUAL = "manual"
    AUTOMATED = "automated"
    PARTNER_FEED = "partner_feed"


class Regulation(Base):
    __tablename__ = "regulations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    regulation_id: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, default=generate_regulation_id
    )
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)  # GDPR, NIS2, EU_AI_ACT
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    jurisdiction: Mapped[str] = mapped_column(String(50), nullable=False, default="EU")
    authority: Mapped[str | None] = mapped_column(String(255), nullable=True)
    current_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    effective_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    review_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[RegulationStatus] = mapped_column(
        pg_enum(RegulationStatus), nullable=False, default=RegulationStatus.ACTIVE
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    last_checked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class RegulationVersion(Base):
    __tablename__ = "regulation_versions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    version_id: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, default=generate_regulation_version_id
    )
    regulation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("regulations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version_number: Mapped[str] = mapped_column(String(20), nullable=False)  # "2018.1", "2024.1"
    version_label: Mapped[str] = mapped_column(String(50), nullable=False)
    effective_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    superseded_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    changes_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    changed_articles: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    impact_level: Mapped[ImpactLevel | None] = mapped_column(pg_enum(ImpactLevel), nullable=True)
    detected_by: Mapped[DetectedBy] = mapped_column(
        pg_enum(DetectedBy), nullable=False, default=DetectedBy.MANUAL
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )