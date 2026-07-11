import io
import json

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from common.auth.clerk import verify_token, TokenClaims
from common.db.session import get_admin_session
from common.models.rule import Rule

from app.config import settings
from app.engine.embeddings import search_rules
from app.limiter import limiter

router = APIRouter(prefix="/api/v1/dpo-assistant", tags=["dpo-assistant"])

SYSTEM_PROMPT = """You are a DPO Assistant for ComplianceKit, a GDPR/NIS2/EU AI Act compliance platform.

Your role: help Data Protection Officers and compliance teams understand their regulatory obligations.

You are provided with relevant regulatory articles as context below. Use them to answer accurately and cite specific article numbers.

Rules:
- Be concise and practical — focus on actionable guidance
- Always cite the relevant article numbers (e.g. "GDPR Art. 17", "NIS2 Art. 23")
- Distinguish between GDPR, NIS2, and EU AI Act requirements when they differ
- If you're unsure, say so — never fabricate regulatory requirements
- This is not legal advice — recommend consulting a lawyer for complex situations"""

ART28_CLAUSES = [
    {"id": "documented_instructions", "label": "Processing only on documented controller instructions (Art. 28(3)(a))"},
    {"id": "confidentiality", "label": "Confidentiality obligations on authorised persons (Art. 28(3)(b))"},
    {"id": "security_measures", "label": "Technical and organisational security measures — Art. 32 (Art. 28(3)(c))"},
    {"id": "sub_processors", "label": "Sub-processor written authorisation and flow-down obligations (Art. 28(2)/(4))"},
    {"id": "data_subject_rights", "label": "Assist controller with data subject rights (Art. 28(3)(e))"},
    {"id": "controller_assistance", "label": "Assist with security, breach notification, DPIA, prior consultation (Art. 28(3)(f))"},
    {"id": "data_deletion", "label": "Delete or return all personal data after services end (Art. 28(3)(g))"},
    {"id": "audit_rights", "label": "Provide compliance information and allow audits (Art. 28(3)(h))"},
    {"id": "processing_details", "label": "Subject matter, duration, nature and purpose of processing specified"},
    {"id": "data_categories", "label": "Types of personal data and categories of data subjects specified"},
]


# ── Schemas ───────────────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    regulation: str | None = None  # "gdpr" | "nis2" | "eu_ai_act" | None (all)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _build_context(rules: list[Rule]) -> str:
    if not rules:
        return ""
    parts = ["--- Relevant regulatory articles ---"]
    for r in rules:
        parts.append(f"\n{r.article}: {r.title or ''}\n{r.description}")
        if r.plain_english:
            parts.append(f"Plain English: {r.plain_english}")
    return "\n".join(parts)


def _stub_contract_analysis() -> dict:
    return {
        "clauses": [
            {**c, "status": "unknown", "note": "AI not configured — set Azure OpenAI credentials to analyse"}
            for c in ART28_CLAUSES
        ],
        "overall_score": 0,
        "summary": "AI analysis requires Azure OpenAI credentials. Set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY in your environment.",
    }


# ── POST /api/v1/dpo-assistant/chat ──────────────────────────────────────────

@router.post("/chat")
@limiter.limit("30/minute")
async def chat(
    request: Request,
    body: ChatRequest,
    claims: TokenClaims = Depends(verify_token),
    session: AsyncSession = Depends(get_admin_session),
):
    # RAG — embed last user message, retrieve relevant rules
    context_rules: list[Rule] = []
    last_user_content = next(
        (m.content for m in reversed(body.messages) if m.role == "user"), ""
    )

    if settings.ai_enabled and last_user_content:
        try:
            regulation_id = None
            if body.regulation:
                from sqlalchemy import select
                from common.models.regulation import Regulation
                result = await session.execute(
                    select(Regulation).where(Regulation.slug == body.regulation)
                )
                reg = result.scalar_one_or_none()
                if reg:
                    regulation_id = reg.id

            context_rules = await search_rules(
                query=last_user_content,
                session=session,
                settings=settings,
                top_k=5,
                regulation_id=regulation_id,
            )
        except Exception:
            pass  # RAG failure → still answer, just without context

    context = _build_context(context_rules)
    system_content = SYSTEM_PROMPT + (f"\n\n{context}" if context else "")

    openai_messages = [{"role": "system", "content": system_content}] + [
        {"role": m.role, "content": m.content} for m in body.messages
    ]

    async def generate():
        if not settings.ai_enabled:
            yield f"data: {json.dumps({'text': 'AI is not configured. Please set up Azure OpenAI credentials (AZURE_OPENAI_ENDPOINT + AZURE_OPENAI_API_KEY) to use the DPO Assistant.'})}\n\n"
            yield "data: [DONE]\n\n"
            return

        from common.ai.client import get_async_client
        client = get_async_client(settings)
        try:
            stream = await client.chat.completions.create(
                model=settings.azure_openai_deployment_gpt4o,
                messages=openai_messages,
                stream=True,
                temperature=0.3,
                max_tokens=1000,
            )
            async for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                if delta:
                    yield f"data: {json.dumps({'text': delta})}\n\n"
        except Exception as exc:
            yield f"data: {json.dumps({'error': str(exc)})}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


# ── POST /api/v1/dpo-assistant/analyse-contract ───────────────────────────────

@router.post("/analyse-contract")
@limiter.limit("30/minute")
async def analyse_contract(
    request: Request,
    file: UploadFile = File(...),
    claims: TokenClaims = Depends(verify_token),
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:  # 10MB limit
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

    if not settings.ai_enabled:
        return _stub_contract_analysis()

    clause_list = "\n".join(
        f'{i+1}. {c["id"]}: {c["label"]}' for i, c in enumerate(ART28_CLAUSES)
    )

    prompt = f"""You are a GDPR compliance expert. Analyse the following Data Processing Agreement (DPA) against GDPR Article 28 mandatory requirements.

For each required clause, determine if it is:
- "covered": clearly and adequately addressed
- "partial": mentioned but incomplete or ambiguous
- "missing": not addressed at all

Required clauses:
{clause_list}

DPA text (first 12000 chars):
{text[:12000]}

Return ONLY a JSON object with this exact structure — no preamble, no markdown:
{{
  "clauses": [
    {{"id": "<id>", "label": "<label>", "status": "covered|partial|missing", "note": "<one-sentence explanation>"}},
    ...
  ],
  "overall_score": <0-100 integer>,
  "summary": "<2-3 sentence executive summary>"
}}"""

    from common.ai.client import get_async_client
    client = get_async_client(settings)
    try:
        resp = await client.chat.completions.create(
            model=settings.azure_openai_deployment_gpt4o,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=2000,
        )
        raw = resp.choices[0].message.content or ""
        # Strip markdown code fences if present
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        result = json.loads(raw.strip())
        return result
    except json.JSONDecodeError:
        raise HTTPException(status_code=502, detail="AI returned malformed response. Try again.")
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI analysis failed: {exc}")
