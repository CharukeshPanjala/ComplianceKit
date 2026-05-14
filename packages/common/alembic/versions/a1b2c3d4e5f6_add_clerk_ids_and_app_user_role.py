"""add clerk ids and app_user role

Revision ID: a1b2c3d4e5f6
Revises: 7f853697f7e2
Create Date: 2026-05-10 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '7f853697f7e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add clerk_org_id to tenants — used to match Clerk webhook events to the right tenant
    op.add_column('tenants', sa.Column(
        'clerk_org_id',
        sa.String(length=64),
        nullable=True,
        unique=True,
    ))

    # Add clerk_user_id to users — used to match Clerk webhook events to the right user
    op.add_column('users', sa.Column(
        'clerk_user_id',
        sa.String(length=64),
        nullable=True,
        unique=True,
    ))

    # Create app_user role — non-superuser so RLS policies are enforced
    # Guard: skip if the role already exists (e.g. test environment created it)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'app_user') THEN
                CREATE ROLE app_user WITH LOGIN PASSWORD 'app_password';
            END IF;
        END $$;
    """)

    op.execute("""
    DO $$
    BEGIN
        EXECUTE 'GRANT CONNECT ON DATABASE ' || current_database() || ' TO app_user';
    END $$;
    """)
    op.execute("GRANT USAGE ON SCHEMA public TO app_user")
    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user")
    op.execute("GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user")
    op.execute("GRANT EXECUTE ON FUNCTION set_tenant_id(TEXT) TO app_user")


def downgrade() -> None:
    op.drop_column('users', 'clerk_user_id')
    op.drop_column('tenants', 'clerk_org_id')

    # Revoke grants before dropping role
    op.execute("REVOKE EXECUTE ON FUNCTION set_tenant_id(TEXT) FROM app_user")
    op.execute("REVOKE ALL ON ALL TABLES IN SCHEMA public FROM app_user")
    op.execute("REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM app_user")
    op.execute("REVOKE USAGE ON SCHEMA public FROM app_user")
    op.execute("""
    DO $$
    BEGIN
        EXECUTE 'REVOKE CONNECT ON DATABASE ' || current_database() || ' FROM app_user';
    END $$;
    """)    
    op.execute("DROP ROLE IF EXISTS app_user")
