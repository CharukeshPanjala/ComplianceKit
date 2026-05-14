# services/api-gateway/tests/test_profile.py

import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from common.db.tenant import get_tenant_session
from common.auth.clerk import TokenClaims, verify_token
from common.models.company_profile import CompanyProfile


FAKE_CLAIMS = TokenClaims(
    user_id="user_abc123",
    tenant_id="ten_xyz456",
    org_role="org:admin",
)


@pytest.fixture
def profile_client():
    """Test client with tenant session + auth overridden."""
    mock_session = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)
    mock_session.add = MagicMock()

    async def override_get_tenant_session():
        yield mock_session

    async def override_verify_token():
        return FAKE_CLAIMS

    app.dependency_overrides[get_tenant_session] = override_get_tenant_session
    app.dependency_overrides[verify_token] = override_verify_token
    yield TestClient(app), mock_session
    app.dependency_overrides.clear()


def make_mock_profile(**kwargs):
    """Build a mock CompanyProfile with sensible defaults."""
    profile = MagicMock(spec=CompanyProfile)
    profile.profile_id = "cp_test001"
    profile.tenant_id = FAKE_CLAIMS.tenant_id
    profile.tenant_name = "Test Corp"
    profile.industry = None
    profile.company_size = None
    profile.b2b_or_b2c = None
    profile.number_of_data_subjects = None
    profile.website_url = None
    profile.primary_jurisdiction = None
    profile.uses_cloud_services = None
    profile.cloud_providers = None
    profile.primary_cloud_region = None
    profile.has_on_premise_servers = None
    profile.certifications = None
    profile.has_compliance_officer = None
    profile.dpo_name = None
    profile.dpo_email = None
    profile.legal_contact_email = None
    profile.data_categories_processed = None
    profile.processing_purposes = None
    profile.data_subject_categories = None
    profile.tech_stack = None
    profile.gdpr_data = None
    profile.nis2_data = None
    profile.ai_act_data = None
    profile.is_complete = False
    for k, v in kwargs.items():
        setattr(profile, k, v)
    return profile


class TestCreateProfile:

    def test_create_profile_returns_201(self, profile_client):
        """POST /profile with valid body → 201, profile_id in response."""
        test_client, mock_session = profile_client
        mock_profile = make_mock_profile()

        # First execute → no existing profile; second → no tenant (optional)
        no_result = MagicMock()
        no_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=no_result)
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()

        # After refresh, the added object should look like mock_profile
        async def fake_refresh(obj):
            obj.profile_id = mock_profile.profile_id
            obj.tenant_id = mock_profile.tenant_id
            obj.tenant_name = mock_profile.tenant_name
            obj.industry = None
            obj.company_size = None
            obj.b2b_or_b2c = None
            obj.number_of_data_subjects = None
            obj.website_url = "https://acme.com"
            obj.primary_jurisdiction = None
            obj.uses_cloud_services = None
            obj.cloud_providers = None
            obj.primary_cloud_region = None
            obj.has_on_premise_servers = None
            obj.certifications = None
            obj.has_compliance_officer = None
            obj.dpo_name = None
            obj.dpo_email = None
            obj.legal_contact_email = None
            obj.data_categories_processed = None
            obj.processing_purposes = None
            obj.data_subject_categories = None
            obj.tech_stack = None
            obj.gdpr_data = None
            obj.nis2_data = None
            obj.ai_act_data = None
            obj.is_complete = False

        mock_session.refresh = fake_refresh

        response = test_client.post(
            "/api/v1/profile",
            json={"website_url": "https://acme.com"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["profile_id"] == "cp_test001"
        assert data["tenant_id"] == FAKE_CLAIMS.tenant_id

    def test_create_profile_409_if_already_exists(self, profile_client):
        """POST /profile when profile exists → 409 Conflict."""
        test_client, mock_session = profile_client
        existing = make_mock_profile()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing
        mock_session.execute = AsyncMock(return_value=mock_result)

        response = test_client.post("/api/v1/profile", json={})

        assert response.status_code == 409
        assert "already exists" in response.json()["detail"].lower()


class TestGetProfile:

    def test_get_profile_returns_200(self, profile_client):
        """GET /profile when profile exists → 200 with profile data."""
        test_client, mock_session = profile_client
        mock_profile = make_mock_profile(website_url="https://acme.com")

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_profile
        mock_session.execute = AsyncMock(return_value=mock_result)

        response = test_client.get("/api/v1/profile")

        assert response.status_code == 200
        data = response.json()
        assert data["profile_id"] == "cp_test001"
        assert data["website_url"] == "https://acme.com"

    def test_get_profile_404_if_not_found(self, profile_client):
        """GET /profile when no profile → 404."""
        test_client, mock_session = profile_client

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        response = test_client.get("/api/v1/profile")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestUpdateProfile:

    def test_patch_profile_returns_200_and_creates_version(self, profile_client):
        """PATCH /profile → 200, version snapshot added to session."""
        test_client, mock_session = profile_client
        mock_profile = make_mock_profile()

        profile_result = MagicMock()
        profile_result.scalar_one_or_none.return_value = mock_profile

        version_result = MagicMock()
        version_scalars = MagicMock()
        version_scalars.first.return_value = None  # no prior versions
        version_result.scalars.return_value = version_scalars

        call_count = 0

        async def side_effect_execute(stmt):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return profile_result
            return version_result

        mock_session.execute = side_effect_execute
        mock_session.flush = AsyncMock()

        async def fake_refresh(obj):
            obj.profile_id = mock_profile.profile_id
            obj.tenant_id = mock_profile.tenant_id
            obj.tenant_name = mock_profile.tenant_name
            obj.industry = None
            obj.company_size = None
            obj.b2b_or_b2c = None
            obj.number_of_data_subjects = None
            obj.website_url = "https://updated.com"
            obj.primary_jurisdiction = None
            obj.uses_cloud_services = None
            obj.cloud_providers = None
            obj.primary_cloud_region = None
            obj.has_on_premise_servers = None
            obj.certifications = None
            obj.has_compliance_officer = None
            obj.dpo_name = None
            obj.dpo_email = None
            obj.legal_contact_email = None
            obj.data_categories_processed = None
            obj.processing_purposes = None
            obj.data_subject_categories = None
            obj.tech_stack = None
            obj.gdpr_data = None
            obj.nis2_data = None
            obj.ai_act_data = None
            obj.is_complete = False

        mock_session.refresh = fake_refresh

        response = test_client.patch(
            "/api/v1/profile",
            json={"website_url": "https://updated.com"},
        )

        assert response.status_code == 200
        assert response.json()["website_url"] == "https://updated.com"
        # only version is db.add()-ed; existing profile is already in session
        assert mock_session.add.call_count == 1

    def test_patch_profile_404_if_not_found(self, profile_client):
        """PATCH /profile when no profile → 404."""
        test_client, mock_session = profile_client

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        response = test_client.patch("/api/v1/profile", json={"website_url": "https://x.com"})

        assert response.status_code == 404