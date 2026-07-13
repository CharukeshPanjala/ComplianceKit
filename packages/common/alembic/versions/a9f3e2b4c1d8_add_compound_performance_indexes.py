"""add compound performance indexes

Revision ID: a9f3e2b4c1d8
Revises: cbbf5b013bae
Create Date: 2026-07-11

"""
from typing import Sequence, Union
from alembic import op

revision: str = "a9f3e2b4c1d8"
down_revision: Union[str, None] = "cbbf5b013bae"
branch_labels: Union[Sequence[str], None] = None
depends_on: Union[Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_gaps_assessment_status",
        "gaps",
        ["assessment_id", "status"],
    )
    op.create_index(
        "ix_gaps_assessment_resolved",
        "gaps",
        ["assessment_id", "resolved"],
    )
    op.create_index(
        "ix_assessments_tenant_regulation",
        "assessments",
        ["tenant_id", "regulation_id"],
    )
    op.create_index(
        "ix_assessments_status",
        "assessments",
        ["status"],
    )


def downgrade() -> None:
    op.drop_index("ix_assessments_status", table_name="assessments")
    op.drop_index("ix_assessments_tenant_regulation", table_name="assessments")
    op.drop_index("ix_gaps_assessment_resolved", table_name="gaps")
    op.drop_index("ix_gaps_assessment_status", table_name="gaps")
