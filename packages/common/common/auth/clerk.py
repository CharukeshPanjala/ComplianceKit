import httpx
import jwt
from cachetools import TTLCache
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

CLERK_JWKS_URL = "https://api.clerk.dev/v1/jwks"

# Cache JWKS for 1 hour — Clerk rotates keys periodically so we cannot cache forever
_jwks_cache: TTLCache = TTLCache(maxsize=1, ttl=3600)

security = HTTPBearer()


class TokenClaims(BaseModel):
    user_id: str        # Clerk user ID — sub claim
    tenant_id: str      # Clerk org_id — maps to our tenant
    org_role: str       # org:admin / org:member / org:viewer


async def _get_jwks(force_refresh: bool = False) -> dict:
    """Fetch Clerk's public keys. Cached for 1 hour, refreshed on demand."""
    if not force_refresh and "jwks" in _jwks_cache:
        return _jwks_cache["jwks"]

    async with httpx.AsyncClient() as client:
        response = await client.get(CLERK_JWKS_URL)
        response.raise_for_status()
        _jwks_cache["jwks"] = response.json()
        return _jwks_cache["jwks"]


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> TokenClaims:
    """
    FastAPI dependency — verifies Clerk JWT on every protected route.

    Returns TokenClaims if valid.
    Raises 401 if token is missing, invalid, expired, or has no org.

    On InvalidTokenError, retries once with a fresh JWKS fetch to handle
    mid-rotation failures gracefully.
    """
    token = credentials.credentials

    try:
        jwks = await _get_jwks()
        claims = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            options={"verify_exp": True},
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError:
        # Key may have rotated — retry once with a fresh fetch
        try:
            jwks = await _get_jwks(force_refresh=True)
            claims = jwt.decode(
                token,
                jwks,
                algorithms=["RS256"],
                options={"verify_exp": True},
            )
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}",
            )

    org_id = claims.get("org_id")
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No organisation found in token — user must belong to an org",
        )

    return TokenClaims(
        user_id=claims["sub"],
        tenant_id=org_id,
        org_role=claims.get("org_role", "org:member"),
    )