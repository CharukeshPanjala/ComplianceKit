"""add_data_role_to_company_profile

Revision ID: 687a949bb0e5
Revises: dd4c036824ba
Create Date: 2026-05-19 14:27:11.263598

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '687a949bb0e5'
down_revision: Union[str, Sequence[str], None] = 'dd4c036824ba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE TYPE datarole AS ENUM ('CONTROLLER', 'PROCESSOR', 'BOTH')")
    op.add_column('company_profiles', sa.Column('data_role', sa.Enum('CONTROLLER', 'PROCESSOR', 'BOTH', name='datarole'), nullable=True))

def downgrade() -> None:
    op.drop_column('company_profiles', 'data_role')
    op.execute("DROP TYPE IF EXISTS datarole")