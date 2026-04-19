import pytest
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from common.auth.clerk import TokenClaims, verify_token

# sample valid claims that Clerk would return
VALID_CLAIMS = {
    "sub": "user_abc123",
    "org_id": "org_xyz789",
    "org_role": "org:admin",
    "exp": 9999999999,
}

class TestVerifyToken:
    """Tests for Clerk JWT verification."""

    @pytest.mark.asyncio
    async def test_valid_token_returns_claims(self):
        """Valid token returns correct TokenClaims."""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="valid.jwt.token"
        )

        with patch("common.auth.clerk._get_jwks", new_callable=AsyncMock) as mock_jwks:
            with patch("common.auth.clerk.jwt.decode", return_value=VALID_CLAIMS):
                mock_jwks.return_value = {"keys": []}
                result = await verify_token(credentials)

        assert isinstance(result, TokenClaims)
        assert result.user_id == "user_abc123"
        assert result.tenant_id == "org_xyz789"
        assert result.org_role == "org:admin"

    @pytest.mark.asyncio
    async def test_expired_token_raises_401(self):
        """Expired token raises 401."""
        import jwt as pyjwt

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="expired.jwt.token"
        )

        with patch("common.auth.clerk._get_jwks", new_callable=AsyncMock) as mock_jwks:
            with patch("common.auth.clerk.jwt.decode",
                      side_effect=pyjwt.ExpiredSignatureError()):
                mock_jwks.return_value = {"keys": []}
                with pytest.raises(HTTPException) as exc:
                    await verify_token(credentials)

        assert exc.value.status_code == 401
        assert "expired" in exc.value.detail.lower()

    @pytest.mark.asyncio
    async def test_invalid_token_raises_401(self):
        """Invalid token raises 401."""
        import jwt as pyjwt

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="invalid.jwt.token"
        )

        with patch("common.auth.clerk._get_jwks", new_callable=AsyncMock) as mock_jwks:
            with patch("common.auth.clerk.jwt.decode",
                      side_effect=pyjwt.InvalidTokenError("bad token")):
                mock_jwks.return_value = {"keys": []}
                with pytest.raises(HTTPException) as exc:
                    await verify_token(credentials)

        assert exc.value.status_code == 401

    @pytest.mark.asyncio
    async def test_token_without_org_raises_401(self):
        """Token with no org_id raises 401 — user must belong to an org."""
        claims_no_org = {
            "sub": "user_abc123",
            "exp": 9999999999,
            # no org_id
        }

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="valid.but.no.org.token"
        )

        with patch("common.auth.clerk._get_jwks", new_callable=AsyncMock) as mock_jwks:
            with patch("common.auth.clerk.jwt.decode", return_value=claims_no_org):
                mock_jwks.return_value = {"keys": []}
                with pytest.raises(HTTPException) as exc:
                    await verify_token(credentials)

        assert exc.value.status_code == 401
        assert "organisation" in exc.value.detail.lower()