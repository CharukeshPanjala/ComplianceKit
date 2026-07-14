"""
COM-211 — Evidence Center API

POST /api/v1/evidence/{document_type}  — upload PDF, evaluate, store
GET  /api/v1/evidence                  — list all documents for tenant
GET  /api/v1/evidence/{document_type}  — latest evaluation for a document type
"""
import io
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from common.auth.clerk import verify_token, TokenClaims
from common.db.session import get_admin_session
from common.models.evidence import DocumentType, EvaluationStatus, EvidenceDocument
from app.engine.evidence_evaluator import EvidenceEvaluator
from app.limiter import limiter

router = APIRouter(prefix="/api/v1/evidence", tags=["evidence"])

_VALID_TYPES = [e.value for e in DocumentType]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _format_doc(doc: EvidenceDocument) -> dict:
    return {
        "evidence_id": doc.evidence_id,
        "document_type": doc.document_type,
        "file_name": doc.file_name,
        "status": doc.status,
        "evaluation_results": doc.evaluation_results,
        "articles_covered": doc.articles_covered,
        "evaluated_at": doc.evaluated_at,
        "created_at": doc.created_at,
    }


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/{document_type}", status_code=200)
@limiter.limit("10/hour")
async def upload_evidence(
    request: Request,
    document_type: str,
    file: UploadFile = File(...),
    claims: TokenClaims = Depends(verify_token),
    session: AsyncSession = Depends(get_admin_session),
):
    """Upload a compliance document PDF, evaluate it, and store the results."""
    if document_type not in _VALID_TYPES:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid document type. Must be one of: {_VALID_TYPES}",
        )

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=422, detail="Only PDF files are supported")

    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="PDF must be under 10MB")

    try:
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(contents))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Failed to read PDF: {exc}")

    if not text.strip():
        raise HTTPException(
            status_code=422,
            detail="PDF appears empty or is a scanned image. Only text-based PDFs are supported.",
        )

    evaluator = EvidenceEvaluator()
    evaluation_results = None
    articles_covered = None
    eval_status = EvaluationStatus.COMPLETED

    try:
        result = await evaluator.evaluate(document_type, text)
        evaluation_results = {
            "overall_status": result.overall_status,
            "clauses": [
                {
                    "article": c.article,
                    "clause_id": c.clause_id,
                    "label": c.label,
                    "status": c.status,
                    "note": c.note,
                }
                for c in result.clauses
            ],
        }
        articles_covered = result.articles_covered
    except Exception:
        eval_status = EvaluationStatus.FAILED

    doc = EvidenceDocument(
        tenant_id=claims.tenant_id,
        document_type=DocumentType(document_type),
        file_name=file.filename,
        extracted_text=text,
        evaluation_results=evaluation_results,
        articles_covered=articles_covered,
        status=eval_status,
        evaluated_at=datetime.now(timezone.utc) if eval_status == EvaluationStatus.COMPLETED else None,
    )
    session.add(doc)
    await session.flush()
    await session.commit()
    await session.refresh(doc)

    return _format_doc(doc)


@router.get("")
async def list_evidence(
    claims: TokenClaims = Depends(verify_token),
    session: AsyncSession = Depends(get_admin_session),
):
    """List all uploaded evidence documents for the tenant."""
    result = await session.execute(
        select(EvidenceDocument)
        .where(EvidenceDocument.tenant_id == claims.tenant_id)
        .order_by(desc(EvidenceDocument.created_at))
    )
    docs = result.scalars().all()
    return {"documents": [_format_doc(d) for d in docs]}


@router.get("/{document_type}")
async def get_evidence_by_type(
    document_type: str,
    claims: TokenClaims = Depends(verify_token),
    session: AsyncSession = Depends(get_admin_session),
):
    """Get the latest uploaded evidence document for a specific type."""
    if document_type not in _VALID_TYPES:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid document type. Must be one of: {_VALID_TYPES}",
        )

    result = await session.execute(
        select(EvidenceDocument)
        .where(
            EvidenceDocument.tenant_id == claims.tenant_id,
            EvidenceDocument.document_type == DocumentType(document_type),
        )
        .order_by(desc(EvidenceDocument.created_at))
        .limit(1)
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="No evidence document found for this type")

    return _format_doc(doc)
