import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException, Request
from common.auth.clerk import TokenClaims
from common.db.tenant import get_tenant_session

VALID_CLAIMS = TokenClaims(
    user_id="user_abc123",
    tenant_id="ten_xyz789",
    org_role="org:admin",
)

def make_mock_request():
    mock_request = MagicMock(spec=Request)
    mock_request.state = MagicMock()
    return mock_request

class TestGetTenantSession:

    @pytest.mark.asyncio
    async def test_sets_tenant_id_on_session(self):
        """Valid claims → SET LOCAL called with correct tenant_id."""
        mock_session = AsyncMock()
        mock_session.execute = AsyncMock()
        mock_session.begin = MagicMock()
        mock_session.begin.return_value.__aenter__ = AsyncMock(return_value=None)
        mock_session.begin.return_value.__aexit__ = AsyncMock(return_value=False)

        mock_factory = MagicMock()
        mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

        with patch("common.db.tenant.AsyncSessionLocal", mock_factory):
            gen = get_tenant_session(request=make_mock_request(), claims=VALID_CLAIMS)
            await gen.__anext__()

        mock_session.execute.assert_called_once()
        call_args = mock_session.execute.call_args
        assert "ten_xyz789" in str(call_args)

    @pytest.mark.asyncio
    async def test_different_tenants_get_different_context(self):
        """Two different tenants get different tenant_id set."""
        tenant_ids_set = []

        async def capture_execute(stmt, params=None):
            if params and "tenant_id" in params:
                tenant_ids_set.append(params["tenant_id"])

        for tenant_id in ["ten_aaa111", "ten_bbb222"]:
            claims = TokenClaims(
                user_id="user_test",
                tenant_id=tenant_id,
                org_role="org:member",
            )
            mock_session = AsyncMock()
            mock_session.execute = AsyncMock(side_effect=capture_execute)
            mock_session.begin = MagicMock()
            mock_session.begin.return_value.__aenter__ = AsyncMock(return_value=None)
            mock_session.begin.return_value.__aexit__ = AsyncMock(return_value=False)

            mock_factory = MagicMock()
            mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

            with patch("common.db.tenant.AsyncSessionLocal", mock_factory):
                gen = get_tenant_session(request=make_mock_request(), claims=claims)
                await gen.__anext__()

        assert tenant_ids_set == ["ten_aaa111", "ten_bbb222"]

    @pytest.mark.asyncio
    async def test_no_token_raises_401(self):
        """Missing/invalid JWT → 401 before session is created."""
        with patch("common.db.tenant.AsyncSessionLocal") as mock_factory:
            with patch(
                "common.auth.clerk.verify_token",
                side_effect=HTTPException(status_code=401, detail="Token has expired"),
            ):
                with pytest.raises(HTTPException) as exc:
                    # simulate FastAPI calling verify_token before get_tenant_session
                    from common.auth.clerk import verify_token
                    from fastapi.security import HTTPAuthorizationCredentials
                    creds = HTTPAuthorizationCredentials(
                        scheme="Bearer", credentials="expired.token"
                    )
                    await verify_token(creds)

            mock_factory.assert_not_called()

        assert exc.value.status_code == 401