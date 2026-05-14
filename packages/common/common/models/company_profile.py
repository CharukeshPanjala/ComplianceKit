import enum
import uuid
from datetime import datetime, date
from sqlalchemy import String, DateTime, Boolean, Date, Integer, func, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from common.models.base import Base
from common.utils.ids import generate_profile_id, generate_profile_version_id


class Industry(enum.Enum):
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    LEGAL = "legal"
    RETAIL = "retail"
    EDUCATION = "education"
    MANUFACTURING = "manufacturing"
    OTHER = "other"


class CompanySize(enum.Enum):
    ONE_TO_TEN = "1-10"
    ELEVEN_TO_FIFTY = "11-50"
    FIFTY_ONE_TO_TWO_HUNDRED = "51-200"
    TWO_HUNDRED_TO_THOUSAND = "201-1000"
    OVER_THOUSAND = "1000+"


class B2BOrB2C(enum.Enum):
    B2B = "b2b"
    B2C = "b2c"
    BOTH = "both"


class NumberOfDataSubjects(enum.Enum):
    UNDER_1K = "under_1k"
    UNDER_10K = "under_10k"
    UNDER_100K = "under_100k"
    OVER_100K = "over_100k"

class CompanyProfile(Base):
    __tablename__ = "company_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    profile_id: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        default=generate_profile_id,
    )
    tenant_id: Mapped[str] = mapped_column(
        String(20),
        ForeignKey("tenants.tenant_id"),
        nullable=False,
        index=True,
    )
    tenant_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    industry: Mapped[Industry | None] = mapped_column(Enum(Industry), nullable=True)
    company_size: Mapped[CompanySize | None] = mapped_column(Enum(CompanySize), nullable=True)
    b2b_or_b2c: Mapped[B2BOrB2C | None] = mapped_column(Enum(B2BOrB2C), nullable=True)
    number_of_data_subjects: Mapped[NumberOfDataSubjects | None] = mapped_column(Enum(NumberOfDataSubjects), nullable=True)
    website_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    primary_jurisdiction: Mapped[str | None] = mapped_column(String(10), nullable=True)
    uses_cloud_services: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    cloud_providers: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    primary_cloud_region: Mapped[str | None] = mapped_column(String(100), nullable=True)
    has_on_premise_servers: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    certifications: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    has_compliance_officer: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    dpo_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    dpo_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    legal_contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    data_categories_processed: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    processing_purposes: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    data_subject_categories: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    tech_stack: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    last_audit_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    previous_regulatory_action: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    regulatory_authority: Mapped[str | None] = mapped_column(String(255), nullable=True)
    gdpr_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    nis2_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    ai_act_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    is_complete: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class CompanyProfileVersion(Base):
    __tablename__ = "company_profile_versions"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    version_id: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        default=generate_profile_version_id,
    )
    tenant_id: Mapped[str] = mapped_column(
        String(20),
        ForeignKey("tenants.tenant_id"),
        nullable=False,
        index=True,
    )
    tenant_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    profile_id: Mapped[str] = mapped_column(
        String(20),
        ForeignKey("company_profiles.profile_id"),
        nullable=False,
        index=True,
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    industry: Mapped[Industry | None] = mapped_column(Enum(Industry), nullable=True)
    company_size: Mapped[CompanySize | None] = mapped_column(Enum(CompanySize), nullable=True)
    gdpr_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    nis2_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    ai_act_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    changed_fields: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    changed_by: Mapped[str | None] = mapped_column(
        String(20),
        ForeignKey("users.user_id"),
        nullable=True,
    )
    change_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )