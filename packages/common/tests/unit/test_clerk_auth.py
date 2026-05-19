import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException, Request

from common.auth.clerk import TokenClaims, verify_token

def make_mock_request():
    """Build a mock FastAPI Request."""
    mock_req = MagicMock(spec=Request)
    mock_req.method = "GET"
    mock_req.url = "http://localhost:3000/api/test"
    mock_req.headers = {}
    return mock_req


def make_mock_state(is_signed_in: bool, payload: dict | None = None, reason: str = ""):
    """Build a mock Clerk request state."""
    state = MagicMock()
    state.is_signed_in = is_signed_in
    state.payload = payload or {}
    state.reason = reason
    return state


class TestVerifyToken:
    """Tests for Clerk JWT verification."""

    @pytest.mark.asyncio
    async def test_valid_token_returns_claims(self):
        """Valid token with org returns correct TokenClaims."""
        mock_state = make_mock_state(
            is_signed_in=True,
            payload={
                "sub": "user_abc123",
                "o": {"id": "org_xyz789", "rol": "org:admin"},
            },
        )

        with patch("common.auth.clerk._clerk.authenticate_request", return_value=mock_state):
            result = await verify_token(make_mock_request())

        assert isinstance(result, TokenClaims)
        assert result.user_id == "user_abc123"
        assert result.tenant_id == "org_xyz789"
        assert result.org_role == "org:admin"

    @pytest.mark.asyncio
    async def test_not_signed_in_raises_401(self):
        """Token that fails Clerk verification raises 401."""
        mock_state = make_mock_state(is_signed_in=False, reason="Token expired")

        with patch("common.auth.clerk._clerk.authenticate_request", return_value=mock_state):
            with pytest.raises(HTTPException) as exc:
                await verify_token(make_mock_request())

        assert exc.value.status_code == 401
        assert "Token expired" in exc.value.detail

    @pytest.mark.asyncio
    async def test_token_without_org_raises_401(self):
        """Token with no org raises 401 — user must belong to an org."""
        mock_state = make_mock_state(
            is_signed_in=True,
            payload={"sub": "user_abc123"},  # no org
        )

        with patch("common.auth.clerk._clerk.authenticate_request", return_value=mock_state):
            with pytest.raises(HTTPException) as exc:
                await verify_token(make_mock_request())

        assert exc.value.status_code == 401
        assert "organisation" in exc.value.detail.lower()

    @pytest.mark.asyncio
    async def test_org_role_defaults_to_member(self):
        """Token with org but no explicit role defaults to org:member."""
        mock_state = make_mock_state(
            is_signed_in=True,
            payload={
                "sub": "user_abc123",
                "o": {"id": "org_xyz789"},  # no rol field
            },
        )

        with patch("common.auth.clerk._clerk.authenticate_request", return_value=mock_state):
            result = await verify_token(make_mock_request())

        assert result.org_role == "org:member"

    @pytest.mark.asyncio
    async def test_legacy_org_id_field_returns_claims(self):
        """Token using legacy org_id field (no 'o' object) → still works."""
        mock_state = make_mock_state(
            is_signed_in=True,
            payload={
                "sub": "user_abc123",
                "org_id": "org_xyz789",
                "org_role": "org:admin",
            },
        )

        with patch("common.auth.clerk._clerk.authenticate_request", return_value=mock_state):
            result = await verify_token(make_mock_request())

        assert result.tenant_id == "org_xyz789"
        assert result.org_role == "org:admin"

    @pytest.mark.asyncio
    async def test_o_field_takes_priority_over_legacy_org_id(self):
        """Token with both 'o' and 'org_id' → 'o.id' wins."""
        mock_state = make_mock_state(
            is_signed_in=True,
            payload={
                "sub": "user_abc123",
                "o": {"id": "org_from_o_field", "rol": "org:admin"},
                "org_id": "org_from_legacy_field",
            },
        )

        with patch("common.auth.clerk._clerk.authenticate_request", return_value=mock_state):
            result = await verify_token(make_mock_request())

        assert result.tenant_id == "org_from_o_field"