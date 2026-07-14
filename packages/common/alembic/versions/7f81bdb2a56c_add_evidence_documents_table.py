"""add_evidence_documents_table

Revision ID: 7f81bdb2a56c
Revises: f1d70da98aeb
Create Date: 2026-07-14 17:53:28.808300

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '7f81bdb2a56c'
down_revision: Union[str, Sequence[str], None] = 'f1d70da98aeb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('evidence_documents',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('evidence_id', sa.String(length=30), nullable=False),
    sa.Column('tenant_id', sa.String(length=50), nullable=False),
    sa.Column('document_type', sa.Enum('privacy_notice', 'security_policy', 'breach_response_plan', 'dpia_template', name='documenttype'), nullable=False),
    sa.Column('file_name', sa.String(length=255), nullable=False),
    sa.Column('extracted_text', sa.Text(), nullable=True),
    sa.Column('evaluation_results', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('articles_covered', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('status', sa.Enum('pending', 'evaluating', 'completed', 'failed', name='evaluationstatus'), nullable=False),
    sa.Column('evaluated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenants.tenant_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('evidence_id')
    )
    op.create_index(op.f('ix_evidence_documents_document_type'), 'evidence_documents', ['document_type'], unique=False)
    op.create_index(op.f('ix_evidence_documents_status'), 'evidence_documents', ['status'], unique=False)
    op.create_index(op.f('ix_evidence_documents_tenant_id'), 'evidence_documents', ['tenant_id'], unique=False)

    op.execute("ALTER TABLE evidence_documents ENABLE ROW LEVEL SECURITY")
    op.execute("""
        CREATE POLICY evidence_documents_tenant_isolation ON evidence_documents
        USING (tenant_id = current_setting('app.current_tenant_id', true))
    """)


def downgrade() -> None:
    op.drop_index(op.f('ix_evidence_documents_tenant_id'), table_name='evidence_documents')
    op.drop_index(op.f('ix_evidence_documents_status'), table_name='evidence_documents')
    op.drop_index(op.f('ix_evidence_documents_document_type'), table_name='evidence_documents')
    op.drop_table('evidence_documents')
    op.execute("DROP TYPE IF EXISTS documenttype")
    op.execute("DROP TYPE IF EXISTS evaluationstatus")
