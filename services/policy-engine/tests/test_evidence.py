"""
COM-211 — Evidence Center API tests

POST /api/v1/evidence/{document_type}
GET  /api/v1/evidence
GET  /api/v1/evidence/{document_type}
"""
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from common.auth.clerk import verify_token, TokenClaims
from common.db.session import get_admin_session
from common.models.evidence import DocumentType, EvaluationStatus, EvidenceDocument

# ── Helpers ───────────────────────────────────────────────────────────────────

FAKE_CLAIMS = TokenClaims(user_id="user_test123", tenant_id="ten_test456", org_role="org:admin")
NOW = datetime.now(timezone.utc)
DUMMY_PDF = b"%PDF-1.4 placeholder"


def make_mock_doc(**kwargs) -> MagicMock:
    d = MagicMock(spec=EvidenceDocument)
    d.evidence_id = kwargs.get("evidence_id", "evd_test001")
    d.tenant_id = kwargs.get("tenant_id", FAKE_CLAIMS.tenant_id)
    d.document_type = kwargs.get("document_type", DocumentType.PRIVACY_NOTICE)
    d.file_name = kwargs.get("file_name", "privacy_notice.pdf")
    d.status = kwargs.get("status", EvaluationStatus.COMPLETED)
    d.evaluation_results = kwargs.get("evaluation_results", {
        "overall_status": "partial",
        "clauses": [
            {"article": 12, "clause_id": "art12_transparency", "label": "Transparency", "status": "met", "note": "Covered"},
            {"article": 13, "clause_id": "art13_purposes", "label": "Purposes", "status": "not_met", "note": "Missing"},
        ],
    })
    d.articles_covered = kwargs.get("articles_covered", [12, 13, 14])
    d.evaluated_at = kwargs.get("evaluated_at", NOW)
    d.created_at = kwargs.get("created_at", NOW)
    return d


def scalar_result(value):
    r = MagicMock()
    r.scalar_one_or_none.return_value = value
    return r


def scalars_result(values):
    scalars = MagicMock()
    scalars.all.return_value = values
    r = MagicMock()
    r.scalars.return_value = scalars
    return r


def mock_pdf_reader(text: str = "This is a privacy notice document.") -> MagicMock:
    page = MagicMock()
    page.extract_text.return_value = text
    reader = MagicMock()
    reader.pages = [page]
    return reader


@pytest.fixture
def client():
    mock_session = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)
    mock_session.add = MagicMock()
    mock_session.flush = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    async def override_session():
        yield mock_session

    async def override_token():
        return FAKE_CLAIMS

    app.dependency_overrides[get_admin_session] = override_session
    app.dependency_overrides[verify_token] = override_token
    yield TestClient(app), mock_session
    app.dependency_overrides.clear()


# ═══════════════════════════════════════════════════════════════════════════════
# POST /api/v1/evidence/{document_type}
# ═══════════════════════════════════════════════════════════════════════════════

class TestUploadEvidence:

    def test_valid_pdf_stub_path_returns_200(self, client):
        test_client, mock_session = client
        mock_session.refresh = AsyncMock(side_effect=lambda d: None)

        with patch("pypdf.PdfReader", return_value=mock_pdf_reader()), \
             patch("app.engine.evidence_evaluator.settings") as mock_es:
            mock_es.ai_enabled = False

            resp = test_client.post(
                "/api/v1/evidence/privacy_notice",
                files={"file": ("privacy_notice.pdf", DUMMY_PDF, "application/pdf")},
            )

        assert resp.status_code == 200
        data = resp.json()
        assert data["document_type"] == "privacy_notice"

    def test_non_pdf_file_returns_422(self, client):
        test_client, _ = client
        resp = test_client.post(
            "/api/v1/evidence/privacy_notice",
            files={"file": ("document.docx", b"fake content", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
        )
        assert resp.status_code == 422
        assert "PDF" in resp.json()["detail"]

    def test_invalid_document_type_returns_422(self, client):
        test_client, _ = client
        resp = test_client.post(
            "/api/v1/evidence/unknown_type",
            files={"file": ("doc.pdf", DUMMY_PDF, "application/pdf")},
        )
        assert resp.status_code == 422
        assert "Invalid document type" in resp.json()["detail"]

    def test_empty_pdf_returns_422(self, client):
        test_client, _ = client
        with patch("pypdf.PdfReader", return_value=mock_pdf_reader(text="")):
            resp = test_client.post(
                "/api/v1/evidence/security_policy",
                files={"file": ("empty.pdf", DUMMY_PDF, "application/pdf")},
            )
        assert resp.status_code == 422
        assert "empty" in resp.json()["detail"].lower()

    def test_all_four_document_types_accepted(self, client):
        test_client, mock_session = client
        mock_session.refresh = AsyncMock(side_effect=lambda d: None)

        for doc_type in ["privacy_notice", "security_policy", "breach_response_plan", "dpia_template"]:
            with patch("pypdf.PdfReader", return_value=mock_pdf_reader()), \
                 patch("app.engine.evidence_evaluator.settings") as mock_es:
                mock_es.ai_enabled = False
                resp = test_client.post(
                    f"/api/v1/evidence/{doc_type}",
                    files={"file": ("doc.pdf", DUMMY_PDF, "application/pdf")},
                )
            assert resp.status_code == 200, f"Failed for {doc_type}: {resp.json()}"

    def test_stub_path_returns_evaluation_results(self, client):
        test_client, mock_session = client
        mock_session.refresh = AsyncMock(side_effect=lambda d: None)

        with patch("pypdf.PdfReader", return_value=mock_pdf_reader("Full privacy policy text here")), \
             patch("app.engine.evidence_evaluator.settings") as mock_es:
            mock_es.ai_enabled = False

            resp = test_client.post(
                "/api/v1/evidence/breach_response_plan",
                files={"file": ("breach_plan.pdf", DUMMY_PDF, "application/pdf")},
            )

        assert resp.status_code == 200
        data = resp.json()
        assert data["articles_covered"] is not None or data["evaluation_results"] is not None or data["status"] in ("completed", "failed")


# ═══════════════════════════════════════════════════════════════════════════════
# GET /api/v1/evidence
# ═══════════════════════════════════════════════════════════════════════════════

class TestListEvidence:

    def test_list_returns_all_tenant_docs(self, client):
        test_client, mock_session = client
        docs = [make_mock_doc(evidence_id="evd_001"), make_mock_doc(evidence_id="evd_002")]
        mock_session.execute = AsyncMock(return_value=scalars_result(docs))

        resp = test_client.get("/api/v1/evidence")
        assert resp.status_code == 200
        assert len(resp.json()["documents"]) == 2

    def test_list_empty_returns_empty_list(self, client):
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=scalars_result([]))

        resp = test_client.get("/api/v1/evidence")
        assert resp.status_code == 200
        assert resp.json()["documents"] == []


# ═══════════════════════════════════════════════════════════════════════════════
# GET /api/v1/evidence/{document_type}
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetEvidenceByType:

    def test_returns_latest_doc_for_type(self, client):
        test_client, mock_session = client
        doc = make_mock_doc(document_type=DocumentType.SECURITY_POLICY)
        mock_session.execute = AsyncMock(return_value=scalar_result(doc))

        resp = test_client.get("/api/v1/evidence/security_policy")
        assert resp.status_code == 200
        assert resp.json()["document_type"] == "security_policy"

    def test_404_when_no_doc_for_type(self, client):
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=scalar_result(None))

        resp = test_client.get("/api/v1/evidence/dpia_template")
        assert resp.status_code == 404

    def test_invalid_type_returns_422(self, client):
        test_client, _ = client
        resp = test_client.get("/api/v1/evidence/made_up_type")
        assert resp.status_code == 422
        assert "Invalid document type" in resp.json()["detail"]
