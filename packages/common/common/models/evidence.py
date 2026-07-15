import enum
import uuid
from datetime import datetime

from sqlalchemy import String, Text, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from common.models.base import Base
from common.utils.enums import pg_enum
from common.utils.ids import generate_evidence_id


class DocumentType(str, enum.Enum):
    PRIVACY_NOTICE = "privacy_notice"
    SECURITY_POLICY = "security_policy"
    BREACH_RESPONSE_PLAN = "breach_response_plan"
    DPIA_TEMPLATE = "dpia_template"


class EvaluationStatus(str, enum.Enum):
    PENDING = "pending"
    EVALUATING = "evaluating"
    COMPLETED = "completed"
    FAILED = "failed"


class EvidenceDocument(Base):
    __tablename__ = "evidence_documents"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    evidence_id: Mapped[str] = mapped_column(
        String(30), unique=True, nullable=False, default=generate_evidence_id
    )
    tenant_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("tenants.tenant_id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    document_type: Mapped[DocumentType] = mapped_column(
        pg_enum(DocumentType), nullable=False, index=True
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    evaluation_results: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    articles_covered: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[EvaluationStatus] = mapped_column(
        pg_enum(EvaluationStatus), nullable=False, default=EvaluationStatus.PENDING, index=True
    )
    evaluated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
