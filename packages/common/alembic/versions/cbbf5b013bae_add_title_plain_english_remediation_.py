"""add_title_plain_english_remediation_hint_to_gaps

Revision ID: cbbf5b013bae
Revises: 12cd2212cee0
Create Date: 2026-06-03 00:15:28.671720

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cbbf5b013bae'
down_revision: Union[str, Sequence[str], None] = '12cd2212cee0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('gaps', sa.Column('title', sa.String(length=500), nullable=True))
    op.add_column('gaps', sa.Column('plain_english', sa.Text(), nullable=True))
    op.add_column('gaps', sa.Column('remediation_hint', sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('gaps', 'remediation_hint')
    op.drop_column('gaps', 'plain_english')
    op.drop_column('gaps', 'title')
