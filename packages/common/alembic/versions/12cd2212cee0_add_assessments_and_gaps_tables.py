"""add_assessments_and_gaps_tables

Revision ID: 12cd2212cee0
Revises: 0cdd1cbf1525
Create Date: 2026-06-02 17:52:07.819614

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '12cd2212cee0'
down_revision: Union[str, Sequence[str], None] = '0cdd1cbf1525'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('assessments',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('assessment_id', sa.String(length=20), nullable=False),
    sa.Column('tenant_id', sa.String(length=50), nullable=False),
    sa.Column('regulation_id', sa.Uuid(), nullable=False),
    sa.Column('regulation_version_id', sa.Uuid(), nullable=True),
    sa.Column('previous_assessment_id', sa.Uuid(), nullable=True),
    sa.Column('status', sa.Enum('pending', 'running', 'completed', 'failed', name='assessmentstatus'), nullable=False),
    sa.Column('score', sa.Integer(), nullable=True),
    sa.Column('risk_level', sa.Enum('low', 'medium', 'high', 'critical', name='risklevel'), nullable=True),
    sa.Column('total_rules', sa.Integer(), nullable=False),
    sa.Column('applicable_rules', sa.Integer(), nullable=False),
    sa.Column('met_rules', sa.Integer(), nullable=False),
    sa.Column('partial_rules', sa.Integer(), nullable=False),
    sa.Column('not_met_rules', sa.Integer(), nullable=False),
    sa.Column('unknown_rules', sa.Integer(), nullable=False),
    sa.Column('profile_snapshot', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('triggered_by', sa.String(length=100), nullable=True),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['previous_assessment_id'], ['assessments.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['regulation_id'], ['regulations.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['regulation_version_id'], ['regulation_versions.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenants.tenant_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('assessment_id')
    )
    op.create_index(op.f('ix_assessments_regulation_id'), 'assessments', ['regulation_id'], unique=False)
    op.create_index(op.f('ix_assessments_regulation_version_id'), 'assessments', ['regulation_version_id'], unique=False)
    op.create_index(op.f('ix_assessments_tenant_id'), 'assessments', ['tenant_id'], unique=False)
    op.create_table('gaps',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('gap_id', sa.String(length=20), nullable=False),
    sa.Column('assessment_id', sa.Uuid(), nullable=False),
    sa.Column('tenant_id', sa.String(length=50), nullable=False),
    sa.Column('rule_id', sa.Uuid(), nullable=False),
    sa.Column('regulation_id', sa.Uuid(), nullable=False),
    sa.Column('regulation_version_id', sa.Uuid(), nullable=True),
    sa.Column('regulation_name', sa.String(length=50), nullable=True),
    sa.Column('article', sa.String(length=100), nullable=True),
    sa.Column('article_number', sa.Integer(), nullable=True),
    sa.Column('chapter', sa.String(length=100), nullable=True),
    sa.Column('category', sa.String(length=100), nullable=True),
    sa.Column('severity', sa.String(length=20), nullable=True),
    sa.Column('fine_tier', sa.String(length=10), nullable=True),
    sa.Column('status', sa.Enum('met', 'partial', 'not_met', 'unknown', 'not_applicable', name='gapstatus'), nullable=False),
    sa.Column('score', sa.Integer(), nullable=True),
    sa.Column('evidence', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('profile_field_value', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('remediation_priority', sa.Enum('critical', 'high', 'medium', 'low', name='remediationpriority'), nullable=True),
    sa.Column('remediation_steps', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('remediation_resources', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('assigned_to', sa.String(length=100), nullable=True),
    sa.Column('due_date', sa.Date(), nullable=True),
    sa.Column('resolved', sa.Boolean(), nullable=False),
    sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('resolved_by', sa.String(length=100), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['assessment_id'], ['assessments.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['regulation_id'], ['regulations.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['regulation_version_id'], ['regulation_versions.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['rule_id'], ['rules.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenants.tenant_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('gap_id')
    )
    op.create_index(op.f('ix_gaps_article_number'), 'gaps', ['article_number'], unique=False)
    op.create_index(op.f('ix_gaps_assessment_id'), 'gaps', ['assessment_id'], unique=False)
    op.create_index(op.f('ix_gaps_category'), 'gaps', ['category'], unique=False)
    op.create_index(op.f('ix_gaps_regulation_id'), 'gaps', ['regulation_id'], unique=False)
    op.create_index(op.f('ix_gaps_remediation_priority'), 'gaps', ['remediation_priority'], unique=False)
    op.create_index(op.f('ix_gaps_resolved'), 'gaps', ['resolved'], unique=False)
    op.create_index(op.f('ix_gaps_rule_id'), 'gaps', ['rule_id'], unique=False)
    op.create_index(op.f('ix_gaps_severity'), 'gaps', ['severity'], unique=False)
    op.create_index(op.f('ix_gaps_status'), 'gaps', ['status'], unique=False)
    op.create_index(op.f('ix_gaps_tenant_id'), 'gaps', ['tenant_id'], unique=False)
    # RLS for assessments
    op.execute("ALTER TABLE assessments ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE assessments FORCE ROW LEVEL SECURITY")
    op.execute("""
        CREATE POLICY tenant_isolation ON assessments
        USING (tenant_id = current_setting('app.tenant_id', true))
    """)
    # RLS for gaps
    op.execute("ALTER TABLE gaps ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE gaps FORCE ROW LEVEL SECURITY")
    op.execute("""
        CREATE POLICY tenant_isolation ON gaps
        USING (tenant_id = current_setting('app.tenant_id', true))
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP POLICY IF EXISTS tenant_isolation ON gaps")
    op.execute("ALTER TABLE gaps DISABLE ROW LEVEL SECURITY")
    op.execute("DROP POLICY IF EXISTS tenant_isolation ON assessments")
    op.execute("ALTER TABLE assessments DISABLE ROW LEVEL SECURITY")
    op.drop_index(op.f('ix_gaps_tenant_id'), table_name='gaps')
    op.drop_index(op.f('ix_gaps_status'), table_name='gaps')
    op.drop_index(op.f('ix_gaps_severity'), table_name='gaps')
    op.drop_index(op.f('ix_gaps_rule_id'), table_name='gaps')
    op.drop_index(op.f('ix_gaps_resolved'), table_name='gaps')
    op.drop_index(op.f('ix_gaps_remediation_priority'), table_name='gaps')
    op.drop_index(op.f('ix_gaps_regulation_id'), table_name='gaps')
    op.drop_index(op.f('ix_gaps_category'), table_name='gaps')
    op.drop_index(op.f('ix_gaps_assessment_id'), table_name='gaps')
    op.drop_index(op.f('ix_gaps_article_number'), table_name='gaps')
    op.drop_table('gaps')
    op.drop_index(op.f('ix_assessments_tenant_id'), table_name='assessments')
    op.drop_index(op.f('ix_assessments_regulation_version_id'), table_name='assessments')
    op.drop_index(op.f('ix_assessments_regulation_id'), table_name='assessments')
    op.drop_table('assessments')
    op.execute("DROP TYPE IF EXISTS gapstatus")
    op.execute("DROP TYPE IF EXISTS remediationpriority")
    op.execute("DROP TYPE IF EXISTS assessmentstatus")
    op.execute("DROP TYPE IF EXISTS risklevel")