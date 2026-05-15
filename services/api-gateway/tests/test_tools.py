import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from common.db.tenant import get_tenant_session
from common.auth.clerk import TokenClaims, verify_token
from common.models.saas_tool import SaasTool


FAKE_CLAIMS = TokenClaims(
    user_id="user_abc123",
    tenant_id="ten_xyz456",
    org_role="org:admin",
)


def make_mock_tool(**kwargs):
    tool = MagicMock(spec=SaasTool)
    tool.tool_id = kwargs.get("tool_id", "tol_test001")
    tool.name = kwargs.get("name", "Stripe")
    tool.category = kwargs.get("category", "payments")
    tool.website_url = kwargs.get("website_url", "https://stripe.com")
    tool.is_active = True
    return tool


@pytest.fixture
def tools_client():
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


class TestListTools:

    def test_get_tools_returns_200(self, tools_client):
        """GET /tools → 200 with list of tools."""
        test_client, mock_session = tools_client

        mock_stripe = make_mock_tool()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_stripe]
        mock_session.execute = AsyncMock(return_value=mock_result)

        response = test_client.get("/api/v1/tools")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Stripe"
        assert data[0]["category"] == "payments"

    def test_get_tools_filtered_by_category(self, tools_client):
        """GET /tools?category=payments → only payment tools."""
        test_client, mock_session = tools_client

        mock_stripe = make_mock_tool(name="Stripe", category="payments")
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_stripe]
        mock_session.execute = AsyncMock(return_value=mock_result)

        response = test_client.get("/api/v1/tools?category=payments")

        assert response.status_code == 200
        data = response.json()
        assert all(t["category"] == "payments" for t in data)

    def test_get_tools_empty_category_returns_empty_list(self, tools_client):
        """GET /tools?category=nonexistent → 200 empty list."""
        test_client, mock_session = tools_client

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        response = test_client.get("/api/v1/tools?category=nonexistent")

        assert response.status_code == 200
        assert response.json() == []


class TestAddTool:

    def test_post_tool_creates_new_tool(self, tools_client):
        """POST /tools with new name → 201, tool created."""
        test_client, mock_session = tools_client

        no_result = MagicMock()
        no_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=no_result)
        mock_session.flush = AsyncMock()

        async def fake_refresh(obj):
            obj.tool_id = "tol_newone1"
            obj.name = "SomeObscureTool"
            obj.category = "other"
            obj.website_url = None

        mock_session.refresh = fake_refresh

        response = test_client.post(
            "/api/v1/tools",
            json={"name": "SomeObscureTool"},
        )

        assert response.status_code == 201
        assert response.json()["name"] == "SomeObscureTool"
        assert response.json()["category"] == "other"

    def test_post_tool_returns_existing_if_duplicate(self, tools_client):
        """POST /tools with existing name (case-insensitive) → 200, existing tool returned."""
        test_client, mock_session = tools_client

        existing = make_mock_tool(name="Stripe", category="payments")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing
        mock_session.execute = AsyncMock(return_value=mock_result)

        response = test_client.post(
            "/api/v1/tools",
            json={"name": "stripe"},  # lowercase — tests case-insensitive dedup
        )

        assert response.status_code == 201  # FastAPI default, frontend ignores it
        assert response.json()["name"] == "Stripe"
        mock_session.add.assert_not_called()

    def test_post_tool_defaults_category_to_other(self, tools_client):
        """POST /tools without category → defaults to 'other'."""
        test_client, mock_session = tools_client

        no_result = MagicMock()
        no_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=no_result)
        mock_session.flush = AsyncMock()

        async def fake_refresh(obj):
            obj.tool_id = "tol_other001"
            obj.name = "CustomTool"
            obj.category = "other"
            obj.website_url = None

        mock_session.refresh = fake_refresh

        response = test_client.post("/api/v1/tools", json={"name": "CustomTool"})

        assert response.status_code == 201
        assert response.json()["category"] == "other"