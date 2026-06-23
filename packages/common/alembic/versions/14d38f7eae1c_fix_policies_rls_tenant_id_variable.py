"""fix_policies_rls_tenant_id_variable

Revision ID: 14d38f7eae1c
Revises: a6d7c5a15e41
Create Date: 2026-06-14 23:19:21.473549

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '14d38f7eae1c'
down_revision: Union[str, Sequence[str], None] = 'a6d7c5a15e41'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("DROP POLICY IF EXISTS tenant_isolation ON policies")
    op.execute("""
        CREATE POLICY tenant_isolation ON policies
        USING (tenant_id = current_setting('app.tenant_id', true))
    """)
    op.execute("ALTER TABLE policies FORCE ROW LEVEL SECURITY")

    op.execute("DROP POLICY IF EXISTS tenant_isolation ON policy_versions")
    op.execute("""
        CREATE POLICY tenant_isolation ON policy_versions
        USING (tenant_id = current_setting('app.tenant_id', true))
    """)
    op.execute("ALTER TABLE policy_versions FORCE ROW LEVEL SECURITY")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("ALTER TABLE policy_versions NO FORCE ROW LEVEL SECURITY")
    op.execute("DROP POLICY IF EXISTS tenant_isolation ON policy_versions")
    op.execute("""
        CREATE POLICY tenant_isolation ON policy_versions
        USING (tenant_id = current_setting('app.current_tenant_id', true))
    """)

    op.execute("ALTER TABLE policies NO FORCE ROW LEVEL SECURITY")
    op.execute("DROP POLICY IF EXISTS tenant_isolation ON policies")
    op.execute("""
        CREATE POLICY tenant_isolation ON policies
        USING (tenant_id = current_setting('app.current_tenant_id', true))
    """)
