# WHAT: Tests for policies API router | CHANGE: add tests for export/pdf, export/docx, status update | WHY: COM-176 — cover download and status-transition endpoints
"""
Tests for policy generation API endpoints:
- POST  /api/v1/policies/generate
- GET   /api/v1/policies
- GET   /api/v1/policies/{policy_id}
- GET   /api/v1/policies/{policy_id}/export/pdf
- GET   /api/v1/policies/{policy_id}/export/docx
- PATCH /api/v1/policies/{policy_id}/status
"""
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from common.auth.clerk import verify_token, TokenClaims
from common.db.session import get_admin_session
from common.models.assessment import Gap
from common.models.company_profile import CompanyProfile
from common.models.policy import (
    Policy, PolicyVersion, PolicyType, PolicyStatus,
    PolicyContentFormat, PolicyChangeType,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

FAKE_CLAIMS = TokenClaims(
    user_id="user_test123",
    tenant_id="ten_test456",
    org_role="org:admin",
)


def make_mock_gap(**kwargs):
    g = MagicMock(spec=Gap)
    g.gap_id = kwargs.get("gap_id", "gap_test001")
    g.tenant_id = kwargs.get("tenant_id", FAKE_CLAIMS.tenant_id)
    g.regulation_id = kwargs.get("regulation_id", uuid.uuid4())
    g.assessment_id = kwargs.get("assessment_id", uuid.uuid4())
    g.regulation_name = kwargs.get("regulation_name", "GDPR")
    g.article = kwargs.get("article", "Article 13")
    g.title = kwargs.get("title", "Privacy notice missing")
    g.plain_english = kwargs.get("plain_english", "You don't have a privacy notice")
    g.remediation_hint = kwargs.get("remediation_hint", "Publish a privacy notice")
    g.severity = kwargs.get("severity", "critical")
    return g


def make_mock_profile(**kwargs):
    p = MagicMock(spec=CompanyProfile)
    p.tenant_id = FAKE_CLAIMS.tenant_id
    p.tenant_name = kwargs.get("tenant_name", "Acme Inc")
    p.industry = kwargs.get("industry", None)
    p.company_size = kwargs.get("company_size", None)
    p.primary_jurisdiction = kwargs.get("primary_jurisdiction", "Ireland")
    p.dpo_name = kwargs.get("dpo_name", "Jane Smith")
    p.dpo_email = kwargs.get("dpo_email", "dpo@example.com")
    p.legal_contact_email = kwargs.get("legal_contact_email", None)
    return p


def make_policy(**kwargs):
    p = Policy(
        tenant_id=FAKE_CLAIMS.tenant_id,
        tenant_name="Acme Inc",
        title="Privacy Notice",
        type=PolicyType.PRIVACY_NOTICE,
        status=PolicyStatus.DRAFT,
        content_format=PolicyContentFormat.MARKDOWN,
        current_version=kwargs.get("current_version", 1),
        content="# old content",
        is_ai_enhanced=False,
        created_by=FAKE_CLAIMS.user_id,
    )
    p.policy_id = kwargs.get("policy_id", "pol_existing1")
    p.created_at = datetime.now(timezone.utc)
    p.updated_at = datetime.now(timezone.utc)
    p.tags = []
    p.related_article = kwargs.get("related_article", "Article 13")
    p.next_review_date = None
    p.language = "en"
    p.regulation_id = kwargs.get("regulation_id", None)
    p.assessment_id = kwargs.get("assessment_id", None)
    return p


def scalar_result(value):
    r = MagicMock()
    r.scalar_one_or_none.return_value = value
    return r


def scalars_result(values):
    scalars = MagicMock()
    scalars.all.return_value = values
    r = MagicMock()
    r.scalars.return_value = scalars
    return r


@pytest.fixture
def client():
    mock_session = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)
    mock_session.commit = AsyncMock()
    mock_session.flush = AsyncMock()
    mock_session.refresh = AsyncMock()

    def add_side_effect(obj):
        if isinstance(obj, Policy) and not obj.policy_id:
            obj.policy_id = "pol_new12345"
            obj.created_at = datetime.now(timezone.utc)
            obj.updated_at = datetime.now(timezone.utc)
        elif isinstance(obj, PolicyVersion) and not obj.version_id:
            obj.version_id = "ver_new12345"
            obj.created_at = datetime.now(timezone.utc)

    mock_session.add = MagicMock(side_effect=add_side_effect)

    async def override_session():
        yield mock_session

    async def override_token():
        return FAKE_CLAIMS

    app.dependency_overrides[get_admin_session] = override_session
    app.dependency_overrides[verify_token] = override_token
    yield TestClient(app), mock_session
    app.dependency_overrides.clear()


# ═══════════════════════════════════════════════════════════════════════════════
# POST /api/v1/policies/generate
# ═══════════════════════════════════════════════════════════════════════════════

class TestGeneratePolicy:

    @patch("app.routers.policies.PolicyGenerator")
    def test_creates_new_policy_and_first_version(self, mock_generator_cls, client):
        test_client, mock_session = client
        mock_generator = AsyncMock()
        mock_generator.generate = AsyncMock(
            return_value=("# Privacy Notice\n\n[TO BE COMPLETED]", False)
        )
        mock_generator_cls.return_value = mock_generator

        gap = make_mock_gap()
        profile = make_mock_profile()
        call_count = 0

        async def side_effect(stmt):
            nonlocal call_count
            call_count += 1
            if call_count == 1:   # gaps
                return scalars_result([gap])
            if call_count == 2:   # profile
                return scalar_result(profile)
            if call_count == 3:   # existing policy
                return scalar_result(None)
            return scalar_result(None)

        mock_session.execute = side_effect

        response = test_client.post(
            "/api/v1/policies/generate",
            json={"policy_type": "privacy_notice", "gap_ids": ["gap_test001"]},
        )

        assert response.status_code == 201
        body = response.json()
        assert body["policy_id"] == "pol_new12345"
        assert body["type"] == "privacy_notice"
        assert body["status"] == "draft"
        assert body["current_version"] == 1
        assert body["is_ai_enhanced"] is False
        assert "[TO BE COMPLETED]" in body["content"]
        mock_session.commit.assert_awaited()

    @patch("app.routers.policies.PolicyGenerator")
    def test_regenerate_existing_policy_increments_version(self, mock_generator_cls, client):
        test_client, mock_session = client
        mock_generator = AsyncMock()
        mock_generator.generate = AsyncMock(return_value=("# Privacy Notice v2", True))
        mock_generator_cls.return_value = mock_generator

        gap = make_mock_gap()
        profile = make_mock_profile()
        existing = make_policy(policy_id="pol_existing1", current_version=2)
        call_count = 0

        async def side_effect(stmt):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return scalars_result([gap])
            if call_count == 2:
                return scalar_result(profile)
            if call_count == 3:
                return scalar_result(existing)
            return scalar_result(None)

        mock_session.execute = side_effect

        response = test_client.post(
            "/api/v1/policies/generate",
            json={"policy_type": "privacy_notice", "gap_ids": ["gap_test001"]},
        )

        assert response.status_code == 201
        body = response.json()
        assert body["policy_id"] == "pol_existing1"
        assert body["current_version"] == 3
        assert body["is_ai_enhanced"] is True
        assert body["content"] == "# Privacy Notice v2"

    def test_invalid_policy_type_returns_422(self, client):
        test_client, _ = client

        response = test_client.post(
            "/api/v1/policies/generate",
            json={"policy_type": "bogus_type", "gap_ids": ["gap_test001"]},
        )

        assert response.status_code == 422

    def test_empty_gap_ids_returns_422(self, client):
        test_client, _ = client

        response = test_client.post(
            "/api/v1/policies/generate",
            json={"policy_type": "privacy_notice", "gap_ids": []},
        )

        assert response.status_code == 422

    def test_no_matching_gaps_returns_404(self, client):
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=scalars_result([]))

        response = test_client.post(
            "/api/v1/policies/generate",
            json={"policy_type": "privacy_notice", "gap_ids": ["gap_nonexistent"]},
        )

        assert response.status_code == 404

    def test_missing_profile_returns_404(self, client):
        test_client, mock_session = client
        gap = make_mock_gap()
        call_count = 0

        async def side_effect(stmt):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return scalars_result([gap])
            return scalar_result(None)  # no profile

        mock_session.execute = side_effect

        response = test_client.post(
            "/api/v1/policies/generate",
            json={"policy_type": "privacy_notice", "gap_ids": ["gap_test001"]},
        )

        assert response.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════════
# GET /api/v1/policies
# ═══════════════════════════════════════════════════════════════════════════════

class TestListPolicies:

    def test_returns_all_tenant_policies(self, client):
        test_client, mock_session = client
        policies = [
            make_policy(policy_id="pol_aaa11111"),
            make_policy(policy_id="pol_bbb22222", current_version=2),
        ]
        mock_session.execute = AsyncMock(return_value=scalars_result(policies))

        response = test_client.get("/api/v1/policies")

        assert response.status_code == 200
        body = response.json()
        assert body["total"] == 2
        assert {p["policy_id"] for p in body["policies"]} == {"pol_aaa11111", "pol_bbb22222"}

    def test_returns_empty_list(self, client):
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=scalars_result([]))

        response = test_client.get("/api/v1/policies")

        assert response.status_code == 200
        assert response.json() == {"total": 0, "policies": []}


# ═══════════════════════════════════════════════════════════════════════════════
# GET /api/v1/policies/{policy_id}
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetPolicy:

    def test_returns_policy_with_versions(self, client):
        test_client, mock_session = client
        policy = make_policy(policy_id="pol_existing1")
        version = PolicyVersion(
            tenant_id=FAKE_CLAIMS.tenant_id,
            policy_id="pol_existing1",
            version_number=1,
            title="Privacy Notice",
            content="# content",
            is_ai_enhanced=False,
            change_type=PolicyChangeType.CREATED,
        )
        version.version_id = "ver_aaa11111"
        version.created_at = datetime.now(timezone.utc)
        call_count = 0

        async def side_effect(stmt):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return scalar_result(policy)
            return scalars_result([version])

        mock_session.execute = side_effect

        response = test_client.get("/api/v1/policies/pol_existing1")

        assert response.status_code == 200
        body = response.json()
        assert body["policy_id"] == "pol_existing1"
        assert len(body["versions"]) == 1
        assert body["versions"][0]["version_id"] == "ver_aaa11111"
        assert body["versions"][0]["change_type"] == "created"

    def test_not_found_returns_404(self, client):
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=scalar_result(None))

        response = test_client.get("/api/v1/policies/pol_nonexistent")

        assert response.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════════
# GET /api/v1/policies/{policy_id}/export/pdf
# ═══════════════════════════════════════════════════════════════════════════════

class TestExportPolicyPdf:

    def test_returns_pdf(self, client):
        test_client, mock_session = client
        policy = make_policy(policy_id="pol_existing1")
        policy.content = "# Privacy Notice\n\n## Who We Are\n\nWe are **Acme Inc**.\n\n- Item one\n- Item two\n\n| Name | Purpose |\n| --- | --- |\n| cookie_a | Session |"
        mock_session.execute = AsyncMock(return_value=scalar_result(policy))

        response = test_client.get("/api/v1/policies/pol_existing1/export/pdf")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert "attachment; filename=privacy_notice.pdf" in response.headers["content-disposition"]
        assert response.content.startswith(b"%PDF")

    def test_not_found_returns_404(self, client):
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=scalar_result(None))

        response = test_client.get("/api/v1/policies/pol_nonexistent/export/pdf")

        assert response.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════════
# GET /api/v1/policies/{policy_id}/export/docx
# ═══════════════════════════════════════════════════════════════════════════════

class TestExportPolicyDocx:

    def test_returns_docx(self, client):
        test_client, mock_session = client
        policy = make_policy(policy_id="pol_existing1")
        policy.content = "# Privacy Notice\n\n## Who We Are\n\nWe are **Acme Inc**.\n\n- Item one\n- Item two\n\n| Name | Purpose |\n| --- | --- |\n| cookie_a | Session |"
        mock_session.execute = AsyncMock(return_value=scalar_result(policy))

        response = test_client.get("/api/v1/policies/pol_existing1/export/docx")

        assert response.status_code == 200
        assert response.headers["content-type"] == (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        assert "attachment; filename=privacy_notice.docx" in response.headers["content-disposition"]
        assert response.content.startswith(b"PK")

    def test_not_found_returns_404(self, client):
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=scalar_result(None))

        response = test_client.get("/api/v1/policies/pol_nonexistent/export/docx")

        assert response.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════════
# PATCH /api/v1/policies/{policy_id}/status
# ═══════════════════════════════════════════════════════════════════════════════

class TestUpdatePolicyStatus:

    def test_draft_to_under_review_updates_status_only(self, client):
        test_client, mock_session = client
        policy = make_policy(policy_id="pol_existing1", current_version=1)
        mock_session.execute = AsyncMock(return_value=scalar_result(policy))

        response = test_client.patch(
            "/api/v1/policies/pol_existing1/status",
            json={"status": "under_review"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "under_review"
        assert body["current_version"] == 1
        assert all(not isinstance(c.args[0], PolicyVersion) for c in mock_session.add.call_args_list)

    def test_transition_to_active_creates_approved_version(self, client):
        test_client, mock_session = client
        policy = make_policy(policy_id="pol_existing1", current_version=1)
        mock_session.execute = AsyncMock(return_value=scalar_result(policy))

        response = test_client.patch(
            "/api/v1/policies/pol_existing1/status",
            json={"status": "active"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "active"
        assert body["current_version"] == 2
        assert body["approved_by"] == FAKE_CLAIMS.user_id
        assert body["approved_at"] is not None

        added_versions = [c.args[0] for c in mock_session.add.call_args_list if isinstance(c.args[0], PolicyVersion)]
        assert len(added_versions) == 1
        assert added_versions[0].change_type == PolicyChangeType.APPROVED
        assert added_versions[0].version_number == 2

    def test_transition_to_archived_creates_archived_version(self, client):
        test_client, mock_session = client
        policy = make_policy(policy_id="pol_existing1", current_version=2)
        mock_session.execute = AsyncMock(return_value=scalar_result(policy))

        response = test_client.patch(
            "/api/v1/policies/pol_existing1/status",
            json={"status": "archived"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "archived"
        assert body["current_version"] == 3
        assert body["approved_by"] is None

        added_versions = [c.args[0] for c in mock_session.add.call_args_list if isinstance(c.args[0], PolicyVersion)]
        assert len(added_versions) == 1
        assert added_versions[0].change_type == PolicyChangeType.ARCHIVED

    def test_invalid_status_returns_422(self, client):
        test_client, mock_session = client
        policy = make_policy(policy_id="pol_existing1")
        mock_session.execute = AsyncMock(return_value=scalar_result(policy))

        response = test_client.patch(
            "/api/v1/policies/pol_existing1/status",
            json={"status": "bogus_status"},
        )

        assert response.status_code == 422

    def test_not_found_returns_404(self, client):
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=scalar_result(None))

        response = test_client.patch(
            "/api/v1/policies/pol_nonexistent/status",
            json={"status": "active"},
        )

        assert response.status_code == 404
