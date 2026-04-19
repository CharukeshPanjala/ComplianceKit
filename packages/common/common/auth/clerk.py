import httpx
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

CLERK_JWKS_URL = "https://api.clerk.dev/v1/jwks"

# cache public keys so we don't fetch on every request
_jwks_cache: dict | None = None

security = HTTPBearer()


class TokenClaims(BaseModel):
    """Verified claims extracted from a valid Clerk JWT."""
    user_id: str        # Clerk user ID — sub claim
    tenant_id: str      # Clerk org_id — maps to our tenant
    org_role: str       # org:admin / org:member / org:viewer


async def _get_jwks() -> dict:
    """Fetch Clerk's public keys. Cached after first fetch."""
    global _jwks_cache
    if _jwks_cache is not None:
        return _jwks_cache

    async with httpx.AsyncClient() as client:
        response = await client.get(CLERK_JWKS_URL)
        response.raise_for_status()
        _jwks_cache = response.json()
        return _jwks_cache


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> TokenClaims:
    """
    FastAPI dependency — verifies Clerk JWT on every protected route.

    Returns TokenClaims if valid.
    Raises 401 if token is missing, invalid, expired, or has no org.
    """
    token = credentials.credentials

    try:
        # fetch Clerk's public keys
        jwks = await _get_jwks()

        # decode and verify the JWT
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
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
        )

    # extract org_id — required for all portal routes
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