from common.models.company_profile import CompanyProfile, CompanyProfileVersion
from common.utils.ids import generate_profile_id, generate_profile_version_id


class TestCompanyProfileIds:

    def test_profile_id_has_correct_prefix(self):
        """Generated profile ID starts with cp_."""
        profile_id = generate_profile_id()
        assert profile_id.startswith("cp_")

    def test_version_id_has_correct_prefix(self):
        """Generated version ID starts with cpv_."""
        version_id = generate_profile_version_id()
        assert version_id.startswith("cpv_")

    def test_profile_id_has_correct_length(self):
        """Generated profile ID has correct total length (cp_ + 8 chars)."""
        profile_id = generate_profile_id()
        assert len(profile_id) == 11  # cp_ (3) + 8 chars

    def test_profile_ids_are_unique(self):
        """Two generated profile IDs are never the same."""
        ids = {generate_profile_id() for _ in range(100)}
        assert len(ids) == 100


class TestCompanyProfileModel:

    def test_profile_defaults_to_incomplete(self):
        """New profile is_complete defaults to False."""
        profile = CompanyProfile(
            tenant_id="ten_test1234",
            profile_id=generate_profile_id(),
        )
        assert not profile.is_complete

    def test_profile_version_has_no_updated_at(self):
        """CompanyProfileVersion has no updated_at — rows are write-once."""
        assert not hasattr(CompanyProfileVersion, "updated_at")