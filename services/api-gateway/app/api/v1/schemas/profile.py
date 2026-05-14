from pydantic import BaseModel
from typing import Any
from common.models.company_profile import (
    Industry,
    CompanySize,
    B2BOrB2C,
    NumberOfDataSubjects,
)


class ProfileCreate(BaseModel):
    """Fields required to create a company profile."""
    industry: Industry | None = None
    company_size: CompanySize | None = None
    b2b_or_b2c: B2BOrB2C | None = None
    number_of_data_subjects: NumberOfDataSubjects | None = None
    website_url: str | None = None
    primary_jurisdiction: str | None = None
    uses_cloud_services: bool | None = None
    cloud_providers: list[str] | None = None
    primary_cloud_region: str | None = None
    has_on_premise_servers: bool | None = None
    certifications: list[str] | None = None
    has_compliance_officer: bool | None = None
    dpo_name: str | None = None
    dpo_email: str | None = None
    legal_contact_email: str | None = None
    data_categories_processed: list[str] | None = None
    processing_purposes: list[str] | None = None
    data_subject_categories: list[str] | None = None
    tech_stack: list[str] | None = None
    gdpr_data: dict[str, Any] | None = None
    nis2_data: dict[str, Any] | None = None
    ai_act_data: dict[str, Any] | None = None


class ProfileUpdate(BaseModel):
    """Fields allowed to be updated on a company profile."""
    industry: Industry | None = None
    company_size: CompanySize | None = None
    b2b_or_b2c: B2BOrB2C | None = None
    number_of_data_subjects: NumberOfDataSubjects | None = None
    website_url: str | None = None
    primary_jurisdiction: str | None = None
    uses_cloud_services: bool | None = None
    cloud_providers: list[str] | None = None
    primary_cloud_region: str | None = None
    has_on_premise_servers: bool | None = None
    certifications: list[str] | None = None
    has_compliance_officer: bool | None = None
    dpo_name: str | None = None
    dpo_email: str | None = None
    legal_contact_email: str | None = None
    data_categories_processed: list[str] | None = None
    processing_purposes: list[str] | None = None
    data_subject_categories: list[str] | None = None
    tech_stack: list[str] | None = None
    gdpr_data: dict[str, Any] | None = None
    nis2_data: dict[str, Any] | None = None
    ai_act_data: dict[str, Any] | None = None
    is_complete: bool | None = None


class ProfileResponse(BaseModel):
    """Shape of the profile returned in API responses."""
    profile_id: str
    tenant_id: str
    tenant_name: str | None
    industry: Industry | None
    company_size: CompanySize | None
    b2b_or_b2c: B2BOrB2C | None
    number_of_data_subjects: NumberOfDataSubjects | None
    website_url: str | None
    primary_jurisdiction: str | None
    uses_cloud_services: bool | None
    cloud_providers: list[str] | None
    primary_cloud_region: str | None
    has_on_premise_servers: bool | None
    certifications: list[str] | None
    has_compliance_officer: bool | None
    dpo_name: str | None
    dpo_email: str | None
    legal_contact_email: str | None
    data_categories_processed: list[str] | None
    processing_purposes: list[str] | None
    data_subject_categories: list[str] | None
    tech_stack: list[str] | None
    gdpr_data: dict[str, Any] | None
    nis2_data: dict[str, Any] | None
    ai_act_data: dict[str, Any] | None
    is_complete: bool

    model_config = {"from_attributes": True}