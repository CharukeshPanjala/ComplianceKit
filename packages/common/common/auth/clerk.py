import httpx
from clerk_backend_api import Clerk
from clerk_backend_api.security.types import AuthenticateRequestOptions
from fastapi import HTTPException, Request, status
from pydantic import BaseModel

from common.config import BaseServiceSettings


class _ClerkSettings(BaseServiceSettings):
    clerk_secret_key: str
    jwt_key: str

_settings = _ClerkSettings()
_clerk = Clerk(bearer_auth=_settings.clerk_secret_key)


class TokenClaims(BaseModel):
    user_id: str
    tenant_id: str
    org_role: str


async def verify_token(request: Request) -> TokenClaims:
    httpx_request = httpx.Request(
        method=request.method,
        url=str(request.url),
        headers=dict(request.headers),
    )

    request_state = _clerk.authenticate_request(
        httpx_request,
        AuthenticateRequestOptions(
            authorized_parties=["http://localhost:3000"],
            jwt_key=_settings.jwt_key,
        )
    )

    if not request_state.is_signed_in:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(request_state.reason),
        )

    payload = request_state.payload or {}
    org = payload.get("o") or {}
    org_id = org.get("id") or payload.get("org_id")
    org_role = org.get("rol") or payload.get("org_role", "org:member")

    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No organisation found in token — user must belong to an org",
        )

    return TokenClaims(
        user_id=payload["sub"],
        tenant_id=org_id,
        org_role=org_role,
    )