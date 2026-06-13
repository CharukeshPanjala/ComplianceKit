"""add_transfer_mechanism_and_special_category_condition_to_ropa

Revision ID: 653d73ea41c8
Revises: 44f5e10e6092
Create Date: 2026-06-09 19:46:20.169098

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '653d73ea41c8'
down_revision: Union[str, Sequence[str], None] = '44f5e10e6092'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE TYPE specialcategorycondition AS ENUM ('explicit_consent', 'employment_law', 'vital_interests', 'non_profit', 'made_public', 'legal_claims', 'public_interest', 'health_care', 'public_health', 'research')")
    op.execute("CREATE TYPE transfermechanism AS ENUM ('scc', 'bcr', 'adequacy_decision', 'derogation', 'none')")
    op.add_column('ropa_entries', sa.Column('special_category_condition', sa.Enum('explicit_consent', 'employment_law', 'vital_interests', 'non_profit', 'made_public', 'legal_claims', 'public_interest', 'health_care', 'public_health', 'research', name='specialcategorycondition'), nullable=True))
    op.add_column('ropa_entries', sa.Column('transfer_mechanism', sa.Enum('scc', 'bcr', 'adequacy_decision', 'derogation', 'none', name='transfermechanism'), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('ropa_entries', 'transfer_mechanism')
    op.drop_column('ropa_entries', 'special_category_condition')
    op.execute("DROP TYPE IF EXISTS transfermechanism")
    op.execute("DROP TYPE IF EXISTS specialcategorycondition")
