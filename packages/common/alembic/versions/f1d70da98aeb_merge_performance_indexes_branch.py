"""merge performance indexes branch

Revision ID: f1d70da98aeb
Revises: 753171fcbb47, a9f3e2b4c1d8
Create Date: 2026-07-14 00:53:06.825907

"""
from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = 'f1d70da98aeb'
down_revision: Union[str, Sequence[str], None] = ('753171fcbb47', 'a9f3e2b4c1d8')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
