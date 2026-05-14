from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from common.db.tenant import get_tenant_session
from common.auth.clerk import TokenClaims, verify_token
from common.models.company_profile import CompanyProfile, CompanyProfileVersion
from common.models.tenant import Tenant
from app.api.v1.schemas.profile import ProfileCreate, ProfileUpdate, ProfileResponse

router = APIRouter()


@router.post("", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    body: ProfileCreate,
    db: AsyncSession = Depends(get_tenant_session),
    claims: TokenClaims = Depends(verify_token),
) -> ProfileResponse:
    """Create a company profile for the current tenant. One profile per tenant."""

    # Check if profile already exists
    existing = await db.execute(
        select(CompanyProfile).where(CompanyProfile.tenant_id == claims.tenant_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Profile already exists for this tenant",
        )

    # Get tenant name for denormalisation
    tenant_result = await db.execute(
        select(Tenant).where(Tenant.tenant_id == claims.tenant_id)
    )
    tenant = tenant_result.scalar_one_or_none()

    profile = CompanyProfile(
        tenant_id=claims.tenant_id,
        tenant_name=tenant.name if tenant else None,
        **body.model_dump(exclude_none=True),
    )
    db.add(profile)
    await db.flush()
    await db.refresh(profile)
    return ProfileResponse.model_validate(profile)


@router.get("", response_model=ProfileResponse)
async def get_profile(
    db: AsyncSession = Depends(get_tenant_session),
    claims: TokenClaims = Depends(verify_token),
) -> ProfileResponse:
    """Get the current tenant's company profile."""
    result = await db.execute(
        select(CompanyProfile).where(CompanyProfile.tenant_id == claims.tenant_id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    return ProfileResponse.model_validate(profile)


@router.patch("", response_model=ProfileResponse)
async def update_profile(
    body: ProfileUpdate,
    db: AsyncSession = Depends(get_tenant_session),
    claims: TokenClaims = Depends(verify_token),
) -> ProfileResponse:
    """Update the current tenant's company profile. Saves a version snapshot before updating."""

    # Fetch existing profile
    result = await db.execute(
        select(CompanyProfile).where(CompanyProfile.tenant_id == claims.tenant_id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    # Get current version number
    version_result = await db.execute(
        select(CompanyProfileVersion).where(
            CompanyProfileVersion.profile_id == profile.profile_id
        ).order_by(CompanyProfileVersion.version_number.desc())
    )
    latest_version = version_result.scalars().first()
    next_version_number = (latest_version.version_number + 1) if latest_version else 1

    # Track which fields are changing
    updates = body.model_dump(exclude_none=True)
    changed_fields = list(updates.keys())

    # Save version snapshot before applying changes
    version = CompanyProfileVersion(
        tenant_id=profile.tenant_id,
        tenant_name=profile.tenant_name,
        profile_id=profile.profile_id,
        version_number=next_version_number,
        industry=profile.industry,
        company_size=profile.company_size,
        gdpr_data=profile.gdpr_data,
        nis2_data=profile.nis2_data,
        ai_act_data=profile.ai_act_data,
        changed_fields=changed_fields,
        changed_by=claims.user_id,
    )
    db.add(version)

    # Apply updates
    for field, value in updates.items():
        setattr(profile, field, value)

    await db.flush()
    await db.refresh(profile)
    return ProfileResponse.model_validate(profile)