from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from common.db.tenant import get_tenant_session
from common.auth.clerk import TokenClaims, verify_token
from common.models.saas_tool import SaasTool
from app.api.v1.schemas.tool import ToolCreate, ToolResponse

router = APIRouter()


@router.get("", response_model=list[ToolResponse])
async def list_tools(
    category: str | None = Query(default=None, description="Filter by category"),
    db: AsyncSession = Depends(get_tenant_session),
    claims: TokenClaims = Depends(verify_token),
) -> list[ToolResponse]:
    """Return all active SaaS tools, optionally filtered by category."""
    stmt = select(SaasTool).where(SaasTool.is_active.is_(True))
    if category:
        stmt = stmt.where(SaasTool.category == category)
    stmt = stmt.order_by(SaasTool.name)

    result = await db.execute(stmt)
    return [ToolResponse.model_validate(t) for t in result.scalars().all()]


@router.post("", response_model=ToolResponse, status_code=201)
async def add_tool(
    body: ToolCreate,
    db: AsyncSession = Depends(get_tenant_session),
    claims: TokenClaims = Depends(verify_token),
) -> ToolResponse:
    """
    Add a custom tool submitted by a user.
    If the tool already exists (case-insensitive), returns the existing one with 200.
    If new, creates it and returns 201.
    """
    result = await db.execute(
        select(SaasTool).where(func.lower(SaasTool.name) == body.name.lower())
    )
    existing = result.scalar_one_or_none()
    if existing:
        return ToolResponse.model_validate(existing)

    tool = SaasTool(
        name=body.name,
        category=body.category,
        website_url=body.website_url,
    )
    db.add(tool)
    await db.flush()
    await db.refresh(tool)
    return ToolResponse.model_validate(tool)