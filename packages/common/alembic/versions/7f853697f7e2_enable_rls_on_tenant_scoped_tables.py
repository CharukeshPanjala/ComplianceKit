"""enable RLS on tenant scoped tables

Revision ID: 7f853697f7e2
Revises: 3b7655cdf4ac
Create Date: 2026-04-18 00:01:19.432720

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7f853697f7e2'
down_revision: Union[str, Sequence[str], None] = '3b7655cdf4ac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the tenant context function
    op.execute("""
        CREATE OR REPLACE FUNCTION set_tenant_id(tenant_id TEXT)
        RETURNS VOID AS $$
        BEGIN
            PERFORM set_config('app.tenant_id', tenant_id, true);
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Enable RLS on tenants table
    op.execute("ALTER TABLE tenants ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE tenants FORCE ROW LEVEL SECURITY")

    # RLS policy for tenants
    op.execute("""
        CREATE POLICY tenant_isolation ON tenants
        USING (tenant_id = current_setting('app.tenant_id', true))
    """)

    # Enable RLS on users table
    op.execute("ALTER TABLE users ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE users FORCE ROW LEVEL SECURITY")

    # RLS policy for users
    op.execute("""
        CREATE POLICY tenant_isolation ON users
        USING (tenant_id = current_setting('app.tenant_id', true))
    """)


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation ON users")
    op.execute("ALTER TABLE users DISABLE ROW LEVEL SECURITY")

    op.execute("DROP POLICY IF EXISTS tenant_isolation ON tenants")
    op.execute("ALTER TABLE tenants DISABLE ROW LEVEL SECURITY")

    op.execute("DROP FUNCTION IF EXISTS set_tenant_id(TEXT)")
