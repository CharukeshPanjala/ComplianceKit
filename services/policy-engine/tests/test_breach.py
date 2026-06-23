"""
Tests for breach tracker API endpoints:
- POST /api/v1/breach
- GET  /api/v1/breach
- GET  /api/v1/breach/{breach_id}
- PATCH /api/v1/breach/{breach_id}
- DELETE /api/v1/breach/{breach_id}
- POST /api/v1/breach/{breach_id}/draft-notification
"""
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.main import app
from common.auth.clerk import verify_token, TokenClaims
from common.db.session import get_admin_session
from common.models.breach import (
    BreachIncident, BreachType, BreachSeverity, BreachStatus, BreachRegulation,
)

# ── Helpers ───────────────────────────────────────────────────────────────────

FAKE_CLAIMS = TokenClaims(user_id="user_test123", tenant_id="ten_test456", org_role="org:admin")

NOW = datetime.now(timezone.utc)


def make_mock_breach(**kwargs):
    b = MagicMock(spec=BreachIncident)
    b.public_id = kwargs.get("public_id", "brc_test001")
    b.tenant_id = kwargs.get("tenant_id", FAKE_CLAIMS.tenant_id)
    b.title = kwargs.get("title", "Unauthorised DB access")
    b.description = kwargs.get("description", "Customer records exposed")
    b.breach_type = kwargs.get("breach_type", BreachType.CONFIDENTIALITY)
    b.severity = kwargs.get("severity", BreachSeverity.HIGH)
    b.regulation = kwargs.get("regulation", BreachRegulation.GDPR)
    b.discovered_at = kwargs.get("discovered_at", NOW)
    b.occurred_at = kwargs.get("occurred_at", None)
    b.reported_at = kwargs.get("reported_at", None)
    b.affected_individual_count = kwargs.get("affected_individual_count", 500)
    b.data_categories_affected = kwargs.get("data_categories_affected", ["email", "name"])
    b.status = kwargs.get("status", BreachStatus.DRAFT)
    b.notification_required = kwargs.get("notification_required", True)
    b.dpa_notified = kwargs.get("dpa_notified", False)
    b.dpa_notification_date = kwargs.get("dpa_notification_date", None)
    b.individuals_notified = kwargs.get("individuals_notified", False)
    b.individuals_notification_date = kwargs.get("individuals_notification_date", None)
    b.containment_measures = kwargs.get("containment_measures", None)
    b.root_cause = kwargs.get("root_cause", None)
    b.remediation_steps = kwargs.get("remediation_steps", None)
    b.ai_notification_draft = kwargs.get("ai_notification_draft", None)
    b.created_at = kwargs.get("created_at", NOW)
    b.updated_at = kwargs.get("updated_at", NOW)
    return b


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
    mock_session.add = MagicMock()
    mock_session.flush = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.delete = AsyncMock()

    async def override_session():
        yield mock_session

    async def override_token():
        return FAKE_CLAIMS

    app.dependency_overrides[get_admin_session] = override_session
    app.dependency_overrides[verify_token] = override_token
    yield TestClient(app), mock_session
    app.dependency_overrides.clear()


# ═══════════════════════════════════════════════════════════════════════════════
# POST /api/v1/breach — create
# ═══════════════════════════════════════════════════════════════════════════════

class TestCreateBreach:

    def _setup_create(self, mock_session, breach=None):
        b = breach or make_mock_breach()

        async def refresh(obj):
            obj.public_id = b.public_id
            obj.title = b.title
            obj.description = b.description
            obj.breach_type = b.breach_type
            obj.severity = b.severity
            obj.regulation = b.regulation
            obj.discovered_at = b.discovered_at
            obj.occurred_at = b.occurred_at
            obj.reported_at = b.reported_at
            obj.affected_individual_count = b.affected_individual_count
            obj.data_categories_affected = b.data_categories_affected
            obj.status = b.status
            obj.notification_required = b.notification_required
            obj.dpa_notified = b.dpa_notified
            obj.dpa_notification_date = b.dpa_notification_date
            obj.individuals_notified = b.individuals_notified
            obj.individuals_notification_date = b.individuals_notification_date
            obj.containment_measures = b.containment_measures
            obj.root_cause = b.root_cause
            obj.remediation_steps = b.remediation_steps
            obj.ai_notification_draft = b.ai_notification_draft
            obj.created_at = b.created_at
            obj.updated_at = b.updated_at

        mock_session.refresh = refresh

    def test_valid_create_returns_201(self, client):
        test_client, mock_session = client
        self._setup_create(mock_session)

        resp = test_client.post("/api/v1/breach", json={
            "title": "Customer data exposed",
            "breach_type": "confidentiality",
            "severity": "high",
            "regulation": "gdpr",
            "discovered_at": NOW.isoformat(),
        })
        assert resp.status_code == 201

    def test_response_contains_deadline_info(self, client):
        test_client, mock_session = client
        self._setup_create(mock_session)

        resp = test_client.post("/api/v1/breach", json={
            "title": "Test breach",
            "breach_type": "integrity",
            "severity": "medium",
            "regulation": "gdpr",
            "discovered_at": NOW.isoformat(),
        })
        assert resp.status_code == 201
        data = resp.json()
        assert "deadline_hours" in data
        assert "deadline_at" in data
        assert "hours_remaining" in data
        assert "deadline_passed" in data

    def test_gdpr_deadline_is_72_hours(self, client):
        test_client, mock_session = client
        self._setup_create(mock_session, make_mock_breach(regulation=BreachRegulation.GDPR))

        resp = test_client.post("/api/v1/breach", json={
            "title": "GDPR breach",
            "breach_type": "confidentiality",
            "severity": "high",
            "regulation": "gdpr",
            "discovered_at": NOW.isoformat(),
        })
        assert resp.json()["deadline_hours"] == 72

    def test_nis2_deadline_is_24_hours(self, client):
        test_client, mock_session = client
        self._setup_create(mock_session, make_mock_breach(regulation=BreachRegulation.NIS2))

        resp = test_client.post("/api/v1/breach", json={
            "title": "NIS2 breach",
            "breach_type": "availability",
            "severity": "high",
            "regulation": "nis2",
            "discovered_at": NOW.isoformat(),
        })
        assert resp.json()["deadline_hours"] == 24

    def test_both_regulation_uses_tightest_24_hour_window(self, client):
        test_client, mock_session = client
        self._setup_create(mock_session, make_mock_breach(regulation=BreachRegulation.BOTH))

        resp = test_client.post("/api/v1/breach", json={
            "title": "Both regulations",
            "breach_type": "combined",
            "severity": "critical",
            "regulation": "both",
            "discovered_at": NOW.isoformat(),
        })
        assert resp.json()["deadline_hours"] == 24

    def test_invalid_breach_type_returns_422(self, client):
        test_client, _ = client

        resp = test_client.post("/api/v1/breach", json={
            "title": "Test",
            "breach_type": "hacking",
            "severity": "high",
            "regulation": "gdpr",
            "discovered_at": NOW.isoformat(),
        })
        assert resp.status_code == 422

    def test_invalid_severity_returns_422(self, client):
        test_client, _ = client

        resp = test_client.post("/api/v1/breach", json={
            "title": "Test",
            "breach_type": "confidentiality",
            "severity": "catastrophic",
            "regulation": "gdpr",
            "discovered_at": NOW.isoformat(),
        })
        assert resp.status_code == 422

    def test_invalid_regulation_returns_422(self, client):
        test_client, _ = client

        resp = test_client.post("/api/v1/breach", json={
            "title": "Test",
            "breach_type": "confidentiality",
            "severity": "high",
            "regulation": "ccpa",
            "discovered_at": NOW.isoformat(),
        })
        assert resp.status_code == 422

    def test_missing_title_returns_422(self, client):
        test_client, _ = client

        resp = test_client.post("/api/v1/breach", json={
            "breach_type": "confidentiality",
            "severity": "high",
            "regulation": "gdpr",
            "discovered_at": NOW.isoformat(),
        })
        assert resp.status_code == 422

    def test_missing_discovered_at_returns_422(self, client):
        test_client, _ = client

        resp = test_client.post("/api/v1/breach", json={
            "title": "Test",
            "breach_type": "confidentiality",
            "severity": "high",
            "regulation": "gdpr",
        })
        assert resp.status_code == 422

    def test_new_breach_has_draft_status(self, client):
        test_client, mock_session = client
        breach = make_mock_breach(status=BreachStatus.DRAFT)
        self._setup_create(mock_session, breach)

        resp = test_client.post("/api/v1/breach", json={
            "title": "New breach",
            "breach_type": "confidentiality",
            "severity": "low",
            "regulation": "gdpr",
            "discovered_at": NOW.isoformat(),
        })
        assert resp.json()["status"] == "draft"

    def test_overdue_breach_deadline_passed_true(self, client):
        test_client, mock_session = client
        old_discovery = NOW - timedelta(hours=100)
        breach = make_mock_breach(regulation=BreachRegulation.GDPR, discovered_at=old_discovery, dpa_notified=False)
        self._setup_create(mock_session, breach)

        resp = test_client.post("/api/v1/breach", json={
            "title": "Old breach",
            "breach_type": "confidentiality",
            "severity": "high",
            "regulation": "gdpr",
            "discovered_at": old_discovery.isoformat(),
        })
        assert resp.json()["deadline_passed"] is True

    def test_notified_breach_deadline_passed_false(self, client):
        """Even if overdue, deadline_passed=False when DPA already notified."""
        test_client, mock_session = client
        old_discovery = NOW - timedelta(hours=100)
        breach = make_mock_breach(regulation=BreachRegulation.GDPR, discovered_at=old_discovery, dpa_notified=True)
        self._setup_create(mock_session, breach)

        resp = test_client.post("/api/v1/breach", json={
            "title": "Old notified breach",
            "breach_type": "confidentiality",
            "severity": "high",
            "regulation": "gdpr",
            "discovered_at": old_discovery.isoformat(),
        })
        assert resp.json()["deadline_passed"] is False


# ═══════════════════════════════════════════════════════════════════════════════
# GET /api/v1/breach
# ═══════════════════════════════════════════════════════════════════════════════

class TestListBreaches:

    def test_returns_empty_list(self, client):
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=scalars_result([]))

        resp = test_client.get("/api/v1/breach")
        assert resp.status_code == 200
        assert resp.json()["total"] == 0
        assert resp.json()["breaches"] == []

    def test_returns_all_tenant_breaches(self, client):
        test_client, mock_session = client
        breaches = [make_mock_breach(), make_mock_breach(public_id="brc_test002")]
        mock_session.execute = AsyncMock(return_value=scalars_result(breaches))

        resp = test_client.get("/api/v1/breach")
        assert resp.json()["total"] == 2

    def test_filter_by_valid_status(self, client):
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=scalars_result([]))

        resp = test_client.get("/api/v1/breach?status=draft")
        assert resp.status_code == 200

    def test_filter_by_invalid_status_returns_422(self, client):
        test_client, _ = client

        resp = test_client.get("/api/v1/breach?status=expired")
        assert resp.status_code == 422

    def test_filter_by_valid_severity(self, client):
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=scalars_result([]))

        resp = test_client.get("/api/v1/breach?severity=critical")
        assert resp.status_code == 200

    def test_filter_by_invalid_severity_returns_422(self, client):
        test_client, _ = client

        resp = test_client.get("/api/v1/breach?severity=extreme")
        assert resp.status_code == 422

    def test_filter_by_valid_regulation(self, client):
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=scalars_result([]))

        resp = test_client.get("/api/v1/breach?regulation=nis2")
        assert resp.status_code == 200

    def test_filter_by_invalid_regulation_returns_422(self, client):
        test_client, _ = client

        resp = test_client.get("/api/v1/breach?regulation=ccpa")
        assert resp.status_code == 422

    def test_response_includes_deadline_fields(self, client):
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=scalars_result([make_mock_breach()]))

        resp = test_client.get("/api/v1/breach")
        item = resp.json()["breaches"][0]
        assert "deadline_hours" in item
        assert "hours_remaining" in item
        assert "deadline_passed" in item


# ═══════════════════════════════════════════════════════════════════════════════
# GET /api/v1/breach/{breach_id}
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetBreach:

    def test_returns_breach(self, client):
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=scalar_result(make_mock_breach()))

        resp = test_client.get("/api/v1/breach/brc_test001")
        assert resp.status_code == 200
        assert resp.json()["breach_id"] == "brc_test001"

    def test_not_found_returns_404(self, client):
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=scalar_result(None))

        resp = test_client.get("/api/v1/breach/brc_unknown")
        assert resp.status_code == 404

    def test_other_tenant_returns_404(self, client):
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=scalar_result(None))

        resp = test_client.get("/api/v1/breach/brc_other_tenant")
        assert resp.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════════
# PATCH /api/v1/breach/{breach_id}
# ═══════════════════════════════════════════════════════════════════════════════

class TestUpdateBreach:

    def test_not_found_returns_404(self, client):
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=scalar_result(None))

        resp = test_client.patch("/api/v1/breach/brc_unknown", json={"status": "under_investigation"})
        assert resp.status_code == 404

    def test_update_status(self, client):
        test_client, mock_session = client
        breach = make_mock_breach(status=BreachStatus.DRAFT)
        mock_session.execute = AsyncMock(return_value=scalar_result(breach))

        resp = test_client.patch("/api/v1/breach/brc_test001", json={"status": "under_investigation"})
        assert resp.status_code == 200
        assert breach.status == BreachStatus.UNDER_INVESTIGATION

    def test_invalid_status_returns_422(self, client):
        test_client, mock_session = client
        breach = make_mock_breach()
        mock_session.execute = AsyncMock(return_value=scalar_result(breach))

        resp = test_client.patch("/api/v1/breach/brc_test001", json={"status": "hacked"})
        assert resp.status_code == 422

    def test_mark_dpa_notified(self, client):
        test_client, mock_session = client
        breach = make_mock_breach(dpa_notified=False)
        mock_session.execute = AsyncMock(return_value=scalar_result(breach))

        resp = test_client.patch("/api/v1/breach/brc_test001", json={"dpa_notified": True})
        assert resp.status_code == 200
        assert breach.dpa_notified is True

    def test_update_affected_count(self, client):
        test_client, mock_session = client
        breach = make_mock_breach(affected_individual_count=None)
        mock_session.execute = AsyncMock(return_value=scalar_result(breach))

        resp = test_client.patch("/api/v1/breach/brc_test001", json={"affected_individual_count": 1200})
        assert resp.status_code == 200
        assert breach.affected_individual_count == 1200

    def test_invalid_breach_type_returns_422(self, client):
        test_client, mock_session = client
        breach = make_mock_breach()
        mock_session.execute = AsyncMock(return_value=scalar_result(breach))

        resp = test_client.patch("/api/v1/breach/brc_test001", json={"breach_type": "cyberattack"})
        assert resp.status_code == 422

    def test_empty_body_changes_nothing(self, client):
        test_client, mock_session = client
        breach = make_mock_breach(title="Original title")
        mock_session.execute = AsyncMock(return_value=scalar_result(breach))

        resp = test_client.patch("/api/v1/breach/brc_test001", json={})
        assert resp.status_code == 200
        assert breach.title == "Original title"

    def test_all_valid_statuses_accepted(self, client):
        valid_statuses = [
            "draft", "under_investigation", "reported_to_dpa",
            "reported_to_individuals", "closed",
        ]
        test_client, mock_session = client

        for status in valid_statuses:
            breach = make_mock_breach()
            mock_session.execute = AsyncMock(return_value=scalar_result(breach))
            resp = test_client.patch("/api/v1/breach/brc_test001", json={"status": status})
            assert resp.status_code == 200, f"Status '{status}' should be valid"


# ═══════════════════════════════════════════════════════════════════════════════
# DELETE /api/v1/breach/{breach_id}
# ═══════════════════════════════════════════════════════════════════════════════

class TestDeleteBreach:

    def test_deletes_existing_breach(self, client):
        test_client, mock_session = client
        breach = make_mock_breach()
        mock_session.execute = AsyncMock(return_value=scalar_result(breach))

        resp = test_client.delete("/api/v1/breach/brc_test001")
        assert resp.status_code == 204
        mock_session.delete.assert_called_once_with(breach)

    def test_not_found_returns_404(self, client):
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=scalar_result(None))

        resp = test_client.delete("/api/v1/breach/brc_unknown")
        assert resp.status_code == 404

    def test_other_tenant_returns_404(self, client):
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=scalar_result(None))

        resp = test_client.delete("/api/v1/breach/brc_other")
        assert resp.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════════
# POST /api/v1/breach/{breach_id}/draft-notification
# ═══════════════════════════════════════════════════════════════════════════════

class TestDraftNotification:

    def test_not_found_returns_404(self, client):
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=scalar_result(None))

        resp = test_client.post("/api/v1/breach/brc_unknown/draft-notification")
        assert resp.status_code == 404

    def test_ai_disabled_returns_stub_draft(self, client):
        test_client, mock_session = client
        breach = make_mock_breach()
        mock_session.execute = AsyncMock(return_value=scalar_result(breach))

        resp = test_client.post("/api/v1/breach/brc_test001/draft-notification")
        assert resp.status_code == 200
        data = resp.json()
        assert "breach_id" in data
        assert "draft" in data
        assert "subject" in data["draft"]
        assert "body" in data["draft"]

    def test_stub_draft_contains_breach_title(self, client):
        test_client, mock_session = client
        breach = make_mock_breach(title="Stripe payment data exposed")
        mock_session.execute = AsyncMock(return_value=scalar_result(breach))

        resp = test_client.post("/api/v1/breach/brc_test001/draft-notification")
        assert "Stripe payment data exposed" in resp.json()["draft"]["subject"]

    def test_stub_draft_body_contains_regulation(self, client):
        test_client, mock_session = client
        breach = make_mock_breach(regulation=BreachRegulation.GDPR)
        mock_session.execute = AsyncMock(return_value=scalar_result(breach))

        resp = test_client.post("/api/v1/breach/brc_test001/draft-notification")
        assert "GDPR" in resp.json()["draft"]["body"]

    def test_stub_draft_saved_to_breach_record(self, client):
        test_client, mock_session = client
        breach = make_mock_breach()
        mock_session.execute = AsyncMock(return_value=scalar_result(breach))

        test_client.post("/api/v1/breach/brc_test001/draft-notification")
        # ai_notification_draft should have been set
        assert breach.ai_notification_draft is not None

    def test_nis2_draft_references_correct_article(self, client):
        test_client, mock_session = client
        breach = make_mock_breach(regulation=BreachRegulation.NIS2)
        mock_session.execute = AsyncMock(return_value=scalar_result(breach))

        resp = test_client.post("/api/v1/breach/brc_test001/draft-notification")
        assert "NIS2" in resp.json()["draft"]["body"]

    def test_both_regulation_draft_references_both(self, client):
        test_client, mock_session = client
        breach = make_mock_breach(regulation=BreachRegulation.BOTH)
        mock_session.execute = AsyncMock(return_value=scalar_result(breach))

        resp = test_client.post("/api/v1/breach/brc_test001/draft-notification")
        body = resp.json()["draft"]["body"]
        assert "GDPR" in body or "NIS2" in body
