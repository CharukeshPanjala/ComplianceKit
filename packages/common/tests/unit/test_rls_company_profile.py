import uuid
import pytest
import pytest_asyncio
from sqlalchemy import text
from common.models.company_profile import CompanyProfile
from common.models.tenant import Tenant, TenantPlan
from common.utils.ids import generate_tenant_id, generate_profile_id


@pytest_asyncio.fixture(scope="session")
async def two_tenant_profiles(db_session):
    """Seed two tenants each with a company profile. Deleted after all tests."""
    await db_session.execute(text("SELECT set_tenant_id('bypass-rls-test')"))

    tenant_a = Tenant(
        id=uuid.uuid4(), tenant_id=generate_tenant_id(),
        name="Profile Tenant A", slug=f"profile-tenant-a-{uuid.uuid4().hex[:6]}",
        plan=TenantPlan.FREE,
    )
    tenant_b = Tenant(
        id=uuid.uuid4(), tenant_id=generate_tenant_id(),
        name="Profile Tenant B", slug=f"profile-tenant-b-{uuid.uuid4().hex[:6]}",
        plan=TenantPlan.FREE,
    )
    db_session.add(tenant_a)
    db_session.add(tenant_b)
    await db_session.flush()

    profile_a = CompanyProfile(
        id=uuid.uuid4(),
        profile_id=generate_profile_id(),
        tenant_id=tenant_a.tenant_id,
        tenant_name=tenant_a.name,
    )
    profile_b = CompanyProfile(
        id=uuid.uuid4(),
        profile_id=generate_profile_id(),
        tenant_id=tenant_b.tenant_id,
        tenant_name=tenant_b.name,
    )
    db_session.add(profile_a)
    db_session.add(profile_b)
    await db_session.commit()

    yield tenant_a, tenant_b, profile_a, profile_b

    # teardown
    await db_session.execute(text("SELECT set_tenant_id('bypass-rls-test')"))
    await db_session.execute(
        text("DELETE FROM company_profiles WHERE tenant_id IN (:a, :b)"),
        {"a": tenant_a.tenant_id, "b": tenant_b.tenant_id}
    )
    await db_session.execute(
        text("DELETE FROM tenants WHERE tenant_id IN (:a, :b)"),
        {"a": tenant_a.tenant_id, "b": tenant_b.tenant_id}
    )
    await db_session.commit()


class TestCompanyProfileRLS:

    @pytest.mark.asyncio
    async def test_tenant_a_cannot_see_tenant_b_profile(self, app_session, two_tenant_profiles):
        """Tenant A cannot see Tenant B's company profile."""
        tenant_a, tenant_b, _, _ = two_tenant_profiles
        await app_session.execute(
            text("SELECT set_tenant_id(:tid)"), {"tid": tenant_a.tenant_id}
        )
        result = await app_session.execute(text("SELECT tenant_id FROM company_profiles"))
        tenant_ids = {row.tenant_id for row in result.fetchall()}

        assert tenant_b.tenant_id not in tenant_ids, \
            "RLS FAILED — Tenant A can see Tenant B profile"
        assert tenant_a.tenant_id in tenant_ids, \
            "RLS ERROR — Tenant A cannot see its own profile"

    @pytest.mark.asyncio
    async def test_tenant_b_cannot_see_tenant_a_profile(self, app_session, two_tenant_profiles):
        """Tenant B cannot see Tenant A's company profile."""
        tenant_a, tenant_b, _, _ = two_tenant_profiles
        await app_session.execute(
            text("SELECT set_tenant_id(:tid)"), {"tid": tenant_b.tenant_id}
        )
        result = await app_session.execute(text("SELECT tenant_id FROM company_profiles"))
        tenant_ids = {row.tenant_id for row in result.fetchall()}

        assert tenant_a.tenant_id not in tenant_ids, \
            "RLS FAILED — Tenant B can see Tenant A profile"
        assert tenant_b.tenant_id in tenant_ids, \
            "RLS ERROR — Tenant B cannot see its own profile"

    @pytest.mark.asyncio
    async def test_invalid_tenant_context_returns_no_profiles(self, app_session):
        """Unknown tenant context returns no profiles."""
        await app_session.execute(
            text("SELECT set_tenant_id(:tid)"), {"tid": "ten_doesnotexist"}
        )
        result = await app_session.execute(text("SELECT * FROM company_profiles"))
        assert len(result.fetchall()) == 0, \
            "RLS FAILED — data returned with invalid tenant context"