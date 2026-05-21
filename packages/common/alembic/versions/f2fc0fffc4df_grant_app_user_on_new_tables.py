"""grant_app_user_on_new_tables

Revision ID: f2fc0fffc4df
Revises: b16e347059d2
Create Date: 2026-05-21 14:16:16.571901

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'f2fc0fffc4df'
down_revision: Union[str, Sequence[str], None] = 'b16e347059d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Backfill: grant on tables created after a1b2c3d4e5f6
    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user")
    op.execute("GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user")

    # Long-term fix: auto-grant to app_user for ALL future tables/sequences created by postgres
    op.execute("""
        ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public
        GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_user
    """)
    op.execute("""
        ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public
        GRANT USAGE, SELECT ON SEQUENCES TO app_user
    """)


def downgrade() -> None:
    op.execute("""
        ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public
        REVOKE SELECT, INSERT, UPDATE, DELETE ON TABLES FROM app_user
    """)
    op.execute("""
        ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public
        REVOKE USAGE, SELECT ON SEQUENCES FROM app_user
    """)