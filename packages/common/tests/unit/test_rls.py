import pytest
from sqlalchemy import text


class TestRLS:
    """Tests proving PostgreSQL RLS isolates tenant data correctly."""

    @pytest.mark.asyncio
    async def test_tenant_a_cannot_see_tenant_b_users(self, app_session, two_tenants):
        tenant_a, tenant_b, _, _ = two_tenants
        await app_session.execute(
            text("SELECT set_tenant_id(:tid)"), {"tid": tenant_a.tenant_id}
        )
        result = await app_session.execute(text("SELECT tenant_id FROM users"))
        tenant_ids = {row.tenant_id for row in result.fetchall()}

        assert tenant_b.tenant_id not in tenant_ids, \
            "RLS FAILED — Tenant A can see Tenant B users"
        assert tenant_a.tenant_id in tenant_ids, \
            "RLS ERROR — Tenant A cannot see its own users"

    @pytest.mark.asyncio
    async def test_tenant_b_cannot_see_tenant_a_users(self, app_session, two_tenants):
        tenant_a, tenant_b, _, _ = two_tenants
        await app_session.execute(
            text("SELECT set_tenant_id(:tid)"), {"tid": tenant_b.tenant_id}
        )
        result = await app_session.execute(text("SELECT tenant_id FROM users"))
        tenant_ids = {row.tenant_id for row in result.fetchall()}

        assert tenant_a.tenant_id not in tenant_ids, \
            "RLS FAILED — Tenant B can see Tenant A users"
        assert tenant_b.tenant_id in tenant_ids, \
            "RLS ERROR — Tenant B cannot see its own users"

    @pytest.mark.asyncio
    async def test_invalid_tenant_context_returns_nothing(self, app_session):
        await app_session.execute(
            text("SELECT set_tenant_id(:tid)"), {"tid": "ten_doesnotexist"}
        )
        result = await app_session.execute(text("SELECT * FROM users"))
        assert len(result.fetchall()) == 0, \
            "RLS FAILED — data returned with invalid tenant context"