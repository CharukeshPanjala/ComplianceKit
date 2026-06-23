"""
Tests for DSAR API endpoints:
- POST /api/v1/dsar
- GET  /api/v1/dsar
- GET  /api/v1/dsar/{dsar_id}
- PATCH /api/v1/dsar/{dsar_id}
- DELETE /api/v1/dsar/{dsar_id}
"""
from datetime import datetime, date, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.main import app
from common.auth.clerk import verify_token, TokenClaims
from common.db.session import get_admin_session
from common.models.dsar import DsarRequest, DsarRequestType, DsarStatus

# ── Helpers ───────────────────────────────────────────────────────────────────

FAKE_CLAIMS = TokenClaims(user_id="user_test123", tenant_id="ten_test456", org_role="org:admin")

NOW = datetime.now(timezone.utc)
TODAY = date.today()


def make_mock_dsar(**kwargs):
    d = MagicMock(spec=DsarRequest)
    d.public_id = kwargs.get("public_id", "dsr_test001")
    d.tenant_id = kwargs.get("tenant_id", FAKE_CLAIMS.tenant_id)
    d.request_type = kwargs.get("request_type", DsarRequestType.ACCESS)
    d.description = kwargs.get("description", None)
    d.requester_email = kwargs.get("requester_email", "john@example.com")
    d.requester_name = kwargs.get("requester_name", "John Smith")
    d.identity_verified = kwargs.get("identity_verified", False)
    d.identity_verification_method = kwargs.get("identity_verification_method", None)
    d.status = kwargs.get("status", DsarStatus.PENDING)
    d.assigned_to = kwargs.get("assigned_to", None)
    d.rejection_reason = kwargs.get("rejection_reason", None)
    d.internal_notes = kwargs.get("internal_notes", None)
    d.received_at = kwargs.get("received_at", NOW)
    d.due_date = kwargs.get("due_date", TODAY + timedelta(days=30))
    d.completed_at = kwargs.get("completed_at", None)
    d.created_at = kwargs.get("created_at", NOW)
    d.updated_at = kwargs.get("updated_at", NOW)
    return d


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
# POST /api/v1/dsar — create
# ═══════════════════════════════════════════════════════════════════════════════

class TestCreateDsar:

    def _setup_create(self, mock_session, dsar=None):
        d = dsar or make_mock_dsar()

        async def refresh(obj):
            obj.public_id = d.public_id
            obj.request_type = d.request_type
            obj.description = d.description
            obj.requester_email = d.requester_email
            obj.requester_name = d.requester_name
            obj.identity_verified = d.identity_verified
            obj.identity_verification_method = d.identity_verification_method
            obj.status = d.status
            obj.assigned_to = d.assigned_to
            obj.rejection_reason = d.rejection_reason
            obj.internal_notes = d.internal_notes
            obj.received_at = d.received_at
            obj.due_date = d.due_date
            obj.completed_at = d.completed_at
            obj.created_at = d.created_at
            obj.updated_at = d.updated_at

        mock_session.refresh = refresh

    def test_valid_create_returns_201(self, client):
        test_client, mock_session = client
        self._setup_create(mock_session)

        resp = test_client.post("/api/v1/dsar", json={
            "request_type": "access",
            "requester_email": "john@example.com",
        })
        assert resp.status_code == 201

    def test_auto_calculates_due_date_30_days(self, client):
        test_client, mock_session = client
        received = NOW
        expected_due = (received.date() + timedelta(days=30)).isoformat()
        dsar = make_mock_dsar(received_at=received, due_date=received.date() + timedelta(days=30))
        self._setup_create(mock_session, dsar)

        resp = test_client.post("/api/v1/dsar", json={
            "request_type": "erasure",
            "requester_email": "jane@example.com",
            "received_at": received.isoformat(),
        })
        assert resp.status_code == 201
        assert resp.json()["due_date"] == expected_due

    def test_received_at_defaults_to_now_when_omitted(self, client):
        test_client, mock_session = client
        self._setup_create(mock_session)

        resp = test_client.post("/api/v1/dsar", json={
            "request_type": "access",
            "requester_email": "test@example.com",
        })
        assert resp.status_code == 201

    def test_invalid_request_type_returns_422(self, client):
        test_client, _ = client

        resp = test_client.post("/api/v1/dsar", json={
            "request_type": "deletion_request",
            "requester_email": "john@example.com",
        })
        assert resp.status_code == 422

    def test_missing_requester_email_returns_422(self, client):
        test_client, _ = client

        resp = test_client.post("/api/v1/dsar", json={
            "request_type": "access",
        })
        assert resp.status_code == 422

    def test_all_request_types_accepted(self, client):
        valid_types = [
            "access", "rectification", "erasure", "portability",
            "restriction", "objection", "withdraw_consent",
        ]
        test_client, mock_session = client

        for rtype in valid_types:
            self._setup_create(mock_session, make_mock_dsar(request_type=DsarRequestType(rtype)))
            resp = test_client.post("/api/v1/dsar", json={
                "request_type": rtype,
                "requester_email": "test@example.com",
            })
            assert resp.status_code == 201, f"Request type '{rtype}' should be valid"

    def test_new_dsar_has_pending_status(self, client):
        test_client, mock_session = client
        self._setup_create(mock_session, make_mock_dsar(status=DsarStatus.PENDING))

        resp = test_client.post("/api/v1/dsar", json={
            "request_type": "access",
            "requester_email": "test@example.com",
        })
        assert resp.json()["status"] == "pending"

    def test_response_contains_days_remaining(self, client):
        test_client, mock_session = client
        self._setup_create(mock_session)

        resp = test_client.post("/api/v1/dsar", json={
            "request_type": "portability",
            "requester_email": "test@example.com",
        })
        data = resp.json()
        assert "days_remaining" in data
        assert "is_overdue" in data

    def test_fresh_dsar_not_overdue(self, client):
        test_client, mock_session = client
        self._setup_create(mock_session, make_mock_dsar(due_date=TODAY + timedelta(days=30)))

        resp = test_client.post("/api/v1/dsar", json={
            "request_type": "access",
            "requester_email": "test@example.com",
        })
        assert resp.json()["is_overdue"] is False
        assert resp.json()["days_remaining"] > 0


# ═══════════════════════════════════════════════════════════════════════════════
# GET /api/v1/dsar
# ═══════════════════════════════════════════════════════════════════════════════

class TestListDsars:

    def test_returns_empty_list(self, client):
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=scalars_result([]))

        resp = test_client.get("/api/v1/dsar")
        assert resp.status_code == 200
        assert resp.json()["total"] == 0
        assert resp.json()["dsars"] == []

    def test_returns_all_tenant_dsars(self, client):
        test_client, mock_session = client
        dsars = [make_mock_dsar(), make_mock_dsar(public_id="dsr_test002")]
        mock_session.execute = AsyncMock(return_value=scalars_result(dsars))

        resp = test_client.get("/api/v1/dsar")
        assert resp.json()["total"] == 2

    def test_filter_by_valid_status(self, client):
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=scalars_result([]))

        resp = test_client.get("/api/v1/dsar?status=pending")
        assert resp.status_code == 200

    def test_filter_by_invalid_status_returns_422(self, client):
        test_client, _ = client

        resp = test_client.get("/api/v1/dsar?status=limbo")
        assert resp.status_code == 422

    def test_filter_by_valid_request_type(self, client):
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=scalars_result([]))

        resp = test_client.get("/api/v1/dsar?request_type=erasure")
        assert resp.status_code == 200

    def test_filter_by_invalid_request_type_returns_422(self, client):
        test_client, _ = client

        resp = test_client.get("/api/v1/dsar?request_type=deletion")
        assert resp.status_code == 422

    def test_sorted_by_due_date_ascending(self, client):
        """Results ordered by due_date ASC — soonest deadline first."""
        test_client, mock_session = client
        urgent = make_mock_dsar(public_id="dsr_urgent", due_date=TODAY + timedelta(days=2))
        later = make_mock_dsar(public_id="dsr_later", due_date=TODAY + timedelta(days=15))
        mock_session.execute = AsyncMock(return_value=scalars_result([urgent, later]))

        resp = test_client.get("/api/v1/dsar")
        ids = [d["dsar_id"] for d in resp.json()["dsars"]]
        assert ids[0] == "dsr_urgent"

    def test_response_includes_deadline_fields(self, client):
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=scalars_result([make_mock_dsar()]))

        resp = test_client.get("/api/v1/dsar")
        item = resp.json()["dsars"][0]
        assert "days_remaining" in item
        assert "is_overdue" in item

    def test_overdue_dsar_flagged(self, client):
        test_client, mock_session = client
        overdue = make_mock_dsar(
            due_date=TODAY - timedelta(days=5),
            status=DsarStatus.PENDING,
        )
        mock_session.execute = AsyncMock(return_value=scalars_result([overdue]))

        resp = test_client.get("/api/v1/dsar")
        item = resp.json()["dsars"][0]
        assert item["is_overdue"] is True
        assert item["days_remaining"] < 0

    def test_terminal_dsar_not_overdue_even_if_past_due(self, client):
        """Completed/rejected/withdrawn DSARs are not flagged as overdue."""
        test_client, mock_session = client

        for terminal_status in [DsarStatus.COMPLETED, DsarStatus.REJECTED, DsarStatus.WITHDRAWN]:
            dsar = make_mock_dsar(
                due_date=TODAY - timedelta(days=10),
                status=terminal_status,
            )
            mock_session.execute = AsyncMock(return_value=scalars_result([dsar]))

            resp = test_client.get("/api/v1/dsar")
            item = resp.json()["dsars"][0]
            assert item["is_overdue"] is False, f"Terminal status '{terminal_status}' should not be overdue"


# ═══════════════════════════════════════════════════════════════════════════════
# GET /api/v1/dsar/{dsar_id}
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetDsar:

    def test_returns_dsar(self, client):
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=scalar_result(make_mock_dsar()))

        resp = test_client.get("/api/v1/dsar/dsr_test001")
        assert resp.status_code == 200
        assert resp.json()["dsar_id"] == "dsr_test001"

    def test_not_found_returns_404(self, client):
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=scalar_result(None))

        resp = test_client.get("/api/v1/dsar/dsr_unknown")
        assert resp.status_code == 404

    def test_other_tenant_returns_404(self, client):
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=scalar_result(None))

        resp = test_client.get("/api/v1/dsar/dsr_other_tenant")
        assert resp.status_code == 404

    def test_contains_request_type_label(self, client):
        test_client, mock_session = client
        dsar = make_mock_dsar(request_type=DsarRequestType.ERASURE)
        mock_session.execute = AsyncMock(return_value=scalar_result(dsar))

        resp = test_client.get("/api/v1/dsar/dsr_test001")
        assert "Art. 17" in resp.json()["request_type_label"]

    def test_requester_email_returned(self, client):
        """PII is returned to authorised tenant users."""
        test_client, mock_session = client
        dsar = make_mock_dsar(requester_email="sensitive@example.com")
        mock_session.execute = AsyncMock(return_value=scalar_result(dsar))

        resp = test_client.get("/api/v1/dsar/dsr_test001")
        assert resp.json()["requester_email"] == "sensitive@example.com"


# ═══════════════════════════════════════════════════════════════════════════════
# PATCH /api/v1/dsar/{dsar_id}
# ═══════════════════════════════════════════════════════════════════════════════

class TestUpdateDsar:

    def test_not_found_returns_404(self, client):
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=scalar_result(None))

        resp = test_client.patch("/api/v1/dsar/dsr_unknown", json={"status": "in_progress"})
        assert resp.status_code == 404

    def test_update_status_to_in_progress(self, client):
        test_client, mock_session = client
        dsar = make_mock_dsar(status=DsarStatus.PENDING)
        mock_session.execute = AsyncMock(return_value=scalar_result(dsar))

        resp = test_client.patch("/api/v1/dsar/dsr_test001", json={"status": "in_progress"})
        assert resp.status_code == 200
        assert dsar.status == DsarStatus.IN_PROGRESS

    def test_completing_auto_sets_completed_at(self, client):
        test_client, mock_session = client
        dsar = make_mock_dsar(status=DsarStatus.IN_PROGRESS, completed_at=None)
        mock_session.execute = AsyncMock(return_value=scalar_result(dsar))

        resp = test_client.patch("/api/v1/dsar/dsr_test001", json={"status": "completed"})
        assert resp.status_code == 200
        assert dsar.completed_at is not None

    def test_completing_already_completed_does_not_overwrite_completed_at(self, client):
        test_client, mock_session = client
        original_completion = NOW - timedelta(hours=2)
        dsar = make_mock_dsar(status=DsarStatus.COMPLETED, completed_at=original_completion)
        mock_session.execute = AsyncMock(return_value=scalar_result(dsar))

        resp = test_client.patch("/api/v1/dsar/dsr_test001", json={"status": "completed"})
        assert resp.status_code == 200
        assert dsar.completed_at == original_completion  # unchanged

    def test_invalid_status_returns_422(self, client):
        test_client, mock_session = client
        dsar = make_mock_dsar()
        mock_session.execute = AsyncMock(return_value=scalar_result(dsar))

        resp = test_client.patch("/api/v1/dsar/dsr_test001", json={"status": "archived"})
        assert resp.status_code == 422

    def test_all_terminal_statuses_accepted(self, client):
        for status in ["completed", "rejected", "withdrawn"]:
            test_client, mock_session = client
            dsar = make_mock_dsar()
            mock_session.execute = AsyncMock(return_value=scalar_result(dsar))

            resp = test_client.patch("/api/v1/dsar/dsr_test001", json={"status": status})
            assert resp.status_code == 200, f"Status '{status}' should be accepted"

    def test_mark_identity_verified(self, client):
        test_client, mock_session = client
        dsar = make_mock_dsar(identity_verified=False)
        mock_session.execute = AsyncMock(return_value=scalar_result(dsar))

        resp = test_client.patch("/api/v1/dsar/dsr_test001", json={
            "identity_verified": True,
            "identity_verification_method": "email confirmation",
        })
        assert resp.status_code == 200
        assert dsar.identity_verified is True
        assert dsar.identity_verification_method == "email confirmation"

    def test_add_rejection_reason(self, client):
        test_client, mock_session = client
        dsar = make_mock_dsar(rejection_reason=None)
        mock_session.execute = AsyncMock(return_value=scalar_result(dsar))

        resp = test_client.patch("/api/v1/dsar/dsr_test001", json={
            "status": "rejected",
            "rejection_reason": "Cannot verify requester identity",
        })
        assert resp.status_code == 200
        assert dsar.rejection_reason == "Cannot verify requester identity"

    def test_add_internal_notes(self, client):
        test_client, mock_session = client
        dsar = make_mock_dsar(internal_notes=None)
        mock_session.execute = AsyncMock(return_value=scalar_result(dsar))

        resp = test_client.patch("/api/v1/dsar/dsr_test001", json={"internal_notes": "Escalated to legal."})
        assert resp.status_code == 200
        assert dsar.internal_notes == "Escalated to legal."

    def test_empty_body_changes_nothing(self, client):
        test_client, mock_session = client
        dsar = make_mock_dsar(status=DsarStatus.PENDING, internal_notes="keep this")
        mock_session.execute = AsyncMock(return_value=scalar_result(dsar))

        resp = test_client.patch("/api/v1/dsar/dsr_test001", json={})
        assert resp.status_code == 200
        assert dsar.status == DsarStatus.PENDING
        assert dsar.internal_notes == "keep this"

    def test_assign_to_user(self, client):
        test_client, mock_session = client
        dsar = make_mock_dsar(assigned_to=None)
        mock_session.execute = AsyncMock(return_value=scalar_result(dsar))

        resp = test_client.patch("/api/v1/dsar/dsr_test001", json={"assigned_to": "user_dpo001"})
        assert resp.status_code == 200
        assert dsar.assigned_to == "user_dpo001"

    def test_other_tenant_returns_404(self, client):
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=scalar_result(None))

        resp = test_client.patch("/api/v1/dsar/dsr_other", json={"status": "in_progress"})
        assert resp.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════════
# DELETE /api/v1/dsar/{dsar_id}
# ═══════════════════════════════════════════════════════════════════════════════

class TestDeleteDsar:

    def test_deletes_existing_dsar(self, client):
        test_client, mock_session = client
        dsar = make_mock_dsar()
        mock_session.execute = AsyncMock(return_value=scalar_result(dsar))

        resp = test_client.delete("/api/v1/dsar/dsr_test001")
        assert resp.status_code == 204
        mock_session.delete.assert_called_once_with(dsar)

    def test_not_found_returns_404(self, client):
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=scalar_result(None))

        resp = test_client.delete("/api/v1/dsar/dsr_unknown")
        assert resp.status_code == 404

    def test_other_tenant_returns_404(self, client):
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=scalar_result(None))

        resp = test_client.delete("/api/v1/dsar/dsr_other")
        assert resp.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════════
# Deadline computation edge cases
# ═══════════════════════════════════════════════════════════════════════════════

class TestDeadlineComputation:

    def test_due_date_is_exactly_30_days_after_received(self, client):
        test_client, mock_session = client
        expected_due = date(2026, 7, 1)

        async def refresh(obj):
            obj.public_id = "dsr_test001"
            obj.request_type = DsarRequestType.ACCESS
            obj.description = None
            obj.requester_email = "test@example.com"
            obj.requester_name = None
            obj.identity_verified = False
            obj.identity_verification_method = None
            obj.status = DsarStatus.PENDING
            obj.assigned_to = None
            obj.rejection_reason = None
            obj.internal_notes = None
            obj.received_at = datetime(2026, 6, 1, tzinfo=timezone.utc)
            obj.due_date = expected_due
            obj.completed_at = None
            obj.created_at = NOW
            obj.updated_at = NOW

        mock_session.refresh = refresh

        resp = test_client.post("/api/v1/dsar", json={
            "request_type": "access",
            "requester_email": "test@example.com",
            "received_at": "2026-06-01T00:00:00Z",
        })
        assert resp.status_code == 201
        assert resp.json()["due_date"] == "2026-07-01"

    def test_days_remaining_positive_for_fresh_dsar(self, client):
        test_client, mock_session = client
        dsar = make_mock_dsar(due_date=TODAY + timedelta(days=25), status=DsarStatus.PENDING)
        mock_session.execute = AsyncMock(return_value=scalar_result(dsar))

        resp = test_client.get("/api/v1/dsar/dsr_test001")
        assert resp.json()["days_remaining"] == 25

    def test_days_remaining_negative_for_overdue(self, client):
        test_client, mock_session = client
        dsar = make_mock_dsar(due_date=TODAY - timedelta(days=3), status=DsarStatus.PENDING)
        mock_session.execute = AsyncMock(return_value=scalar_result(dsar))

        resp = test_client.get("/api/v1/dsar/dsr_test001")
        assert resp.json()["days_remaining"] == -3
        assert resp.json()["is_overdue"] is True
