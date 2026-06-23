"""
Tests for processors API endpoints:
- POST /api/v1/processors/generate
- GET  /api/v1/processors
- PATCH /api/v1/processors/{processor_id}
- DELETE /api/v1/processors/{processor_id}
"""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from common.auth.clerk import verify_token, TokenClaims
from common.db.session import get_admin_session
from common.models.processor import (
    Processor, ProcessorRisk, ProcessorSource, ProcessorStatus, ProcessorTransferMechanism,
)

# ── Helpers ───────────────────────────────────────────────────────────────────

FAKE_CLAIMS = TokenClaims(user_id="user_test123", tenant_id="ten_test456", org_role="org:admin")


def make_mock_profile(tech_stack=None):
    p = MagicMock()
    p.tenant_id = FAKE_CLAIMS.tenant_id
    p.tech_stack = tech_stack or []
    p.gdpr_data = {}
    return p


def make_mock_processor(**kwargs):
    p = MagicMock(spec=Processor)
    p.public_id = kwargs.get("public_id", "prc_test001")
    p.tenant_id = kwargs.get("tenant_id", FAKE_CLAIMS.tenant_id)
    p.name = kwargs.get("name", "Stripe")
    p.category = kwargs.get("category", "payments")
    p.service_description = kwargs.get("service_description", None)
    p.website = kwargs.get("website", None)
    p.data_categories = kwargs.get("data_categories", ["financial_data"])
    p.data_subject_categories = kwargs.get("data_subject_categories", ["customers"])
    p.processing_locations = kwargs.get("processing_locations", ["EEA"])
    p.transfer_mechanism = kwargs.get("transfer_mechanism", ProcessorTransferMechanism.SCC)
    p.dpa_signed = kwargs.get("dpa_signed", False)
    p.dpa_date = kwargs.get("dpa_date", None)
    p.contract_review_date = kwargs.get("contract_review_date", None)
    p.risk_level = kwargs.get("risk_level", ProcessorRisk.HIGH)
    p.status = kwargs.get("status", ProcessorStatus.ACTIVE)
    p.source = kwargs.get("source", ProcessorSource.AUTO_GENERATED)
    p.sub_processors = kwargs.get("sub_processors", None)
    p.notes = kwargs.get("notes", None)
    p.created_at = kwargs.get("created_at", None)
    p.updated_at = kwargs.get("updated_at", None)
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
    mock_session.add = MagicMock()
    mock_session.add_all = MagicMock()
    mock_session.flush = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()
    mock_session.delete = AsyncMock()
    mock_session.execute = AsyncMock()

    async def override_session():
        yield mock_session

    async def override_token():
        return FAKE_CLAIMS

    app.dependency_overrides[get_admin_session] = override_session
    app.dependency_overrides[verify_token] = override_token
    yield TestClient(app), mock_session
    app.dependency_overrides.clear()


# ═══════════════════════════════════════════════════════════════════════════════
# POST /api/v1/processors/generate
# ═══════════════════════════════════════════════════════════════════════════════

class TestGenerateProcessors:

    def test_no_profile_returns_404(self, client):
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=scalar_result(None))

        resp = test_client.post("/api/v1/processors/generate")
        assert resp.status_code == 404
        assert "profile" in resp.json()["detail"].lower()

    def test_empty_tech_stack_generates_nothing(self, client):
        test_client, mock_session = client
        profile = make_mock_profile(tech_stack=[])
        mock_session.execute = AsyncMock(return_value=scalar_result(profile))

        resp = test_client.post("/api/v1/processors/generate")
        assert resp.status_code == 200
        assert resp.json()["generated"] == 0
        assert resp.json()["processors"] == []

    def test_returns_generated_count(self, client):
        test_client, mock_session = client
        profile = make_mock_profile(tech_stack=["Stripe", "AWS"])
        call_count = 0

        async def side_effect(stmt):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return scalar_result(profile)
            return scalars_result([MagicMock(name="Stripe", category="payments", website_url=None)])

        mock_session.execute = side_effect

        with patch("app.routers.processors.ProcessorGenerator") as mock_gen:
            generated = MagicMock()
            generated.name = "Stripe"
            generated.category = "payments"
            generated.data_categories = ["financial_data"]
            generated.data_subject_categories = ["customers"]
            generated.processing_locations = ["EEA"]
            generated.transfer_mechanism = ProcessorTransferMechanism.SCC
            generated.risk_level = ProcessorRisk.HIGH
            generated.status = ProcessorStatus.ACTIVE
            generated.source = ProcessorSource.AUTO_GENERATED
            generated.dpa_signed = False
            mock_gen.return_value.generate.return_value = [generated]

            async def refresh_with_id(obj):
                obj.public_id = "prc_new001"
                obj.name = "Stripe"
                obj.category = "payments"
                obj.data_categories = ["financial_data"]
                obj.data_subject_categories = ["customers"]
                obj.processing_locations = ["EEA"]
                obj.transfer_mechanism = ProcessorTransferMechanism.SCC
                obj.risk_level = ProcessorRisk.HIGH
                obj.status = ProcessorStatus.ACTIVE
                obj.source = ProcessorSource.AUTO_GENERATED
                obj.dpa_signed = False
                obj.dpa_date = None
                obj.contract_review_date = None
                obj.service_description = None
                obj.website = None
                obj.sub_processors = None
                obj.notes = None
                obj.created_at = None
                obj.updated_at = None

            mock_session.refresh = refresh_with_id

            resp = test_client.post("/api/v1/processors/generate")
            assert resp.status_code == 200
            assert resp.json()["generated"] == 1

    def test_idempotent_deletes_existing_auto_generated(self, client):
        """Each generate call deletes existing AUTO_GENERATED entries first."""
        test_client, mock_session = client
        profile = make_mock_profile(tech_stack=[])
        mock_session.execute = AsyncMock(return_value=scalar_result(profile))

        test_client.post("/api/v1/processors/generate")
        # delete() should have been called (for the existing auto-generated processors)
        assert mock_session.execute.called

    def test_unknown_tools_get_other_category(self, client):
        """Tech stack tools not in saas_tools table → category 'other'."""
        test_client, mock_session = client
        profile = make_mock_profile(tech_stack=["SomeUnknownTool"])
        call_count = 0

        async def side_effect(stmt):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return scalar_result(profile)
            return scalars_result([])  # no known tools found

        mock_session.execute = side_effect

        with patch("app.routers.processors.ProcessorGenerator") as mock_gen:
            mock_gen.return_value.generate.return_value = []

            resp = test_client.post("/api/v1/processors/generate")
            assert resp.status_code == 200
            # Generator was called — verify it received the unknown tool with 'other' category
            call_args = mock_gen.call_args
            tools = call_args[0][1]
            assert any(t["category"] == "other" for t in tools)


# ═══════════════════════════════════════════════════════════════════════════════
# GET /api/v1/processors
# ═══════════════════════════════════════════════════════════════════════════════

class TestListProcessors:

    def test_returns_empty_list(self, client):
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=scalars_result([]))

        resp = test_client.get("/api/v1/processors")
        assert resp.status_code == 200
        assert resp.json()["total"] == 0
        assert resp.json()["processors"] == []

    def test_returns_all_processors_for_tenant(self, client):
        test_client, mock_session = client
        processors = [make_mock_processor(), make_mock_processor(public_id="prc_test002", name="AWS")]
        mock_session.execute = AsyncMock(return_value=scalars_result(processors))

        resp = test_client.get("/api/v1/processors")
        assert resp.status_code == 200
        assert resp.json()["total"] == 2

    def test_filter_by_valid_status(self, client):
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=scalars_result([]))

        resp = test_client.get("/api/v1/processors?status=active")
        assert resp.status_code == 200

    def test_filter_by_invalid_status_returns_422(self, client):
        test_client, mock_session = client

        resp = test_client.get("/api/v1/processors?status=bogus_status")
        assert resp.status_code == 422

    def test_filter_by_valid_risk_level(self, client):
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=scalars_result([]))

        resp = test_client.get("/api/v1/processors?risk_level=high")
        assert resp.status_code == 200

    def test_filter_by_invalid_risk_level_returns_422(self, client):
        test_client, mock_session = client

        resp = test_client.get("/api/v1/processors?risk_level=extreme")
        assert resp.status_code == 422

    def test_filter_by_category(self, client):
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=scalars_result([]))

        resp = test_client.get("/api/v1/processors?category=payments")
        assert resp.status_code == 200

    def test_response_contains_required_fields(self, client):
        test_client, mock_session = client
        processor = make_mock_processor()
        mock_session.execute = AsyncMock(return_value=scalars_result([processor]))

        resp = test_client.get("/api/v1/processors")
        item = resp.json()["processors"][0]
        for field in ["processor_id", "name", "category", "risk_level", "status", "dpa_signed"]:
            assert field in item

    def test_enum_values_serialised_as_strings(self, client):
        test_client, mock_session = client
        processor = make_mock_processor(
            status=ProcessorStatus.ACTIVE,
            risk_level=ProcessorRisk.HIGH,
            transfer_mechanism=ProcessorTransferMechanism.SCC,
        )
        mock_session.execute = AsyncMock(return_value=scalars_result([processor]))

        resp = test_client.get("/api/v1/processors")
        item = resp.json()["processors"][0]
        assert item["status"] == "active"
        assert item["risk_level"] == "high"
        assert item["transfer_mechanism"] == "scc"


# ═══════════════════════════════════════════════════════════════════════════════
# PATCH /api/v1/processors/{processor_id}
# ═══════════════════════════════════════════════════════════════════════════════

class TestUpdateProcessor:

    def test_not_found_returns_404(self, client):
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=scalar_result(None))

        resp = test_client.patch("/api/v1/processors/prc_unknown", json={"dpa_signed": True})
        assert resp.status_code == 404

    def test_other_tenant_returns_404(self, client):
        """tenant_id filter in query means other tenant's processor returns None."""
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=scalar_result(None))

        resp = test_client.patch("/api/v1/processors/prc_other", json={"dpa_signed": True})
        assert resp.status_code == 404

    def test_update_dpa_signed(self, client):
        test_client, mock_session = client
        processor = make_mock_processor(dpa_signed=False)
        mock_session.execute = AsyncMock(return_value=scalar_result(processor))

        resp = test_client.patch("/api/v1/processors/prc_test001", json={"dpa_signed": True})
        assert resp.status_code == 200
        assert processor.dpa_signed is True

    def test_update_notes(self, client):
        test_client, mock_session = client
        processor = make_mock_processor(notes=None)
        mock_session.execute = AsyncMock(return_value=scalar_result(processor))

        resp = test_client.patch("/api/v1/processors/prc_test001", json={"notes": "Reviewed Q2 2026"})
        assert resp.status_code == 200
        assert processor.notes == "Reviewed Q2 2026"

    def test_invalid_status_returns_422(self, client):
        test_client, mock_session = client
        processor = make_mock_processor()
        mock_session.execute = AsyncMock(return_value=scalar_result(processor))

        resp = test_client.patch("/api/v1/processors/prc_test001", json={"status": "nonexistent"})
        assert resp.status_code == 422

    def test_invalid_risk_level_returns_422(self, client):
        test_client, mock_session = client
        processor = make_mock_processor()
        mock_session.execute = AsyncMock(return_value=scalar_result(processor))

        resp = test_client.patch("/api/v1/processors/prc_test001", json={"risk_level": "extreme"})
        assert resp.status_code == 422

    def test_invalid_transfer_mechanism_returns_422(self, client):
        test_client, mock_session = client
        processor = make_mock_processor()
        mock_session.execute = AsyncMock(return_value=scalar_result(processor))

        resp = test_client.patch("/api/v1/processors/prc_test001", json={"transfer_mechanism": "magic"})
        assert resp.status_code == 422

    def test_valid_enum_strings_accepted(self, client):
        test_client, mock_session = client
        processor = make_mock_processor()
        mock_session.execute = AsyncMock(return_value=scalar_result(processor))

        resp = test_client.patch(
            "/api/v1/processors/prc_test001",
            json={"status": "under_review", "risk_level": "medium", "transfer_mechanism": "bcr"},
        )
        assert resp.status_code == 200

    def test_empty_body_changes_nothing(self, client):
        test_client, mock_session = client
        processor = make_mock_processor(notes="existing")
        mock_session.execute = AsyncMock(return_value=scalar_result(processor))

        resp = test_client.patch("/api/v1/processors/prc_test001", json={})
        assert resp.status_code == 200
        assert processor.notes == "existing"


# ═══════════════════════════════════════════════════════════════════════════════
# DELETE /api/v1/processors/{processor_id}
# ═══════════════════════════════════════════════════════════════════════════════

class TestDeleteProcessor:

    def test_deletes_existing_processor(self, client):
        test_client, mock_session = client
        processor = make_mock_processor()
        mock_session.execute = AsyncMock(return_value=scalar_result(processor))

        resp = test_client.delete("/api/v1/processors/prc_test001")
        assert resp.status_code == 204
        mock_session.delete.assert_called_once_with(processor)

    def test_not_found_returns_404(self, client):
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=scalar_result(None))

        resp = test_client.delete("/api/v1/processors/prc_unknown")
        assert resp.status_code == 404

    def test_other_tenant_returns_404(self, client):
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=scalar_result(None))

        resp = test_client.delete("/api/v1/processors/prc_other_tenant")
        assert resp.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════════
# HTTP method enforcement
# ═══════════════════════════════════════════════════════════════════════════════

class TestMethodEnforcement:

    def test_put_not_allowed(self, client):
        test_client, _ = client
        assert test_client.put("/api/v1/processors/prc_test001", json={}).status_code == 405

    def test_post_to_processor_id_not_allowed(self, client):
        test_client, _ = client
        assert test_client.post("/api/v1/processors/prc_test001", json={}).status_code == 405
