# WHAT: Unit tests for RopaGenerator engine | CHANGE: new file | WHY: COM-172 — verify generator logic
import pytest
from app.engine.ropa_generator import RopaGenerator
from common.models.ropa import RopaDataRole, RopaLegalBasis, TransferMechanism, SpecialCategoryCondition


def make_profile(**kwargs) -> dict:
    return {
        "data_role": "controller",
        "data_categories_processed": ["email", "name"],
        "processing_purposes": ["marketing", "analytics"],
        "data_subject_categories": ["customers"],
        "tech_stack": ["Salesforce", "Google Analytics"],
        "uses_cloud_services": True,
        "cloud_providers": ["aws", "gcp"],
        "primary_jurisdiction": "IE",
        "company_size": "51-200",
        "number_of_data_subjects": "under_10k",
        "gdpr_data": {
            "lawful_bases": ["consent", "legitimate_interests"],
            "transfers_outside_eea": False,
            "uses_data_processors": True,
        },
        "ai_act_data": {},
        **kwargs,
    }


def test_generates_one_entry_per_purpose():
    profile = make_profile(processing_purposes=["marketing", "analytics", "hr_management"])
    entries = RopaGenerator(profile).generate()
    assert len(entries) == 3


def test_known_purpose_maps_correctly():
    entries = RopaGenerator(make_profile(processing_purposes=["marketing"])).generate()
    e = entries[0]
    assert e.activity_name == "Marketing and Communications"
    assert e.category == "marketing"
    assert e.legal_basis == RopaLegalBasis.CONSENT


def test_unknown_purpose_uses_title_case_fallback():
    entries = RopaGenerator(make_profile(processing_purposes=["custom_workflow"])).generate()
    e = entries[0]
    assert e.activity_name == "Custom Workflow"
    assert e.legal_basis == RopaLegalBasis.LEGITIMATE_INTERESTS


def test_data_role_controller():
    entries = RopaGenerator(make_profile(data_role="controller")).generate()
    assert entries[0].data_role == RopaDataRole.CONTROLLER


def test_data_role_processor():
    entries = RopaGenerator(make_profile(data_role="processor")).generate()
    assert entries[0].data_role == RopaDataRole.PROCESSOR


def test_data_role_both_maps_to_controller():
    entries = RopaGenerator(make_profile(data_role="both")).generate()
    assert entries[0].data_role == RopaDataRole.CONTROLLER


def test_single_lawful_basis_overrides_all():
    profile = make_profile(
        processing_purposes=["marketing", "analytics"],
        gdpr_data={"lawful_bases": ["contract"], "transfers_outside_eea": False},
    )
    entries = RopaGenerator(profile).generate()
    assert all(e.legal_basis == RopaLegalBasis.CONTRACT for e in entries)


def test_no_special_category_data():
    entries = RopaGenerator(make_profile(data_categories_processed=["email", "name"])).generate()
    e = entries[0]
    assert e.has_special_category_data is False
    assert e.special_category_condition is None
    assert e.special_category_types == []


def test_has_special_category_data():
    entries = RopaGenerator(make_profile(data_categories_processed=["email", "health"])).generate()
    e = entries[0]
    assert e.has_special_category_data is True
    assert "health" in e.special_category_types
    assert e.special_category_condition == SpecialCategoryCondition.EXPLICIT_CONSENT


def test_requires_dpia_false_when_small_scale():
    profile = make_profile(
        data_categories_processed=["health"],
        number_of_data_subjects="under_1k",
    )
    entries = RopaGenerator(profile).generate()
    assert entries[0].requires_dpia is False


def test_requires_dpia_true_when_special_and_large_scale():
    profile = make_profile(
        data_categories_processed=["health"],
        number_of_data_subjects="over_100k",
    )
    entries = RopaGenerator(profile).generate()
    assert entries[0].requires_dpia is True


def test_transfer_mechanism_none_when_no_transfers():
    profile = make_profile(gdpr_data={"transfers_outside_eea": False, "lawful_bases": ["consent"]})
    entries = RopaGenerator(profile).generate()
    assert entries[0].transfer_mechanism == TransferMechanism.NONE


def test_transfer_mechanism_scc_when_transfers_outside_eea():
    profile = make_profile(gdpr_data={"transfers_outside_eea": True, "lawful_bases": ["consent"]})
    entries = RopaGenerator(profile).generate()
    assert entries[0].transfer_mechanism == TransferMechanism.SCC


def test_processing_locations_includes_jurisdiction_and_cloud():
    profile = make_profile(
        primary_jurisdiction="IE",
        uses_cloud_services=True,
        cloud_providers=["aws", "gcp"],
    )
    entries = RopaGenerator(profile).generate()
    locations = entries[0].processing_locations
    assert "IE" in locations
    assert "aws" in locations
    assert "gcp" in locations


def test_processing_locations_no_cloud():
    profile = make_profile(primary_jurisdiction="DE", uses_cloud_services=False)
    entries = RopaGenerator(profile).generate()
    assert entries[0].processing_locations == ["DE"]


def test_empty_purposes_generates_fallback():
    profile = make_profile(processing_purposes=[])
    entries = RopaGenerator(profile).generate()
    assert len(entries) == 1
    assert entries[0].purpose == "data_processing"
