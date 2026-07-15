"""
COM-211 — Evidence Evaluator

Evaluates uploaded compliance documents against GDPR article checklists.
Returns per-clause status and article coverage for each document type.
"""
import json
from dataclasses import dataclass

from app.config import settings


# ── Clause definitions per document type ─────────────────────────────────────

_DOCUMENT_SPECS: dict[str, dict] = {
    "privacy_notice": {
        "articles": [12, 13, 14],
        "clauses": [
            {"article": 12, "id": "art12_transparency", "label": "Transparent, concise and intelligible communication of processing information"},
            {"article": 13, "id": "art13_identity", "label": "Identity and contact details of controller and DPO (if any)"},
            {"article": 13, "id": "art13_purposes", "label": "Purposes and lawful basis for each processing activity"},
            {"article": 13, "id": "art13_retention", "label": "Retention period or criteria for determining it"},
            {"article": 13, "id": "art13_rights", "label": "Data subject rights (access, erasure, portability, objection)"},
            {"article": 13, "id": "art13_third_parties", "label": "Recipients or categories of recipients of personal data"},
            {"article": 14, "id": "art14_source", "label": "Source from which personal data originates (when not collected directly)"},
            {"article": 14, "id": "art14_categories", "label": "Categories of personal data concerned (when not collected directly)"},
        ],
    },
    "security_policy": {
        "articles": [32],
        "clauses": [
            {"article": 32, "id": "art32_pseudonymisation", "label": "Pseudonymisation and encryption of personal data"},
            {"article": 32, "id": "art32_confidentiality", "label": "Ongoing confidentiality, integrity, availability and resilience of processing systems"},
            {"article": 32, "id": "art32_restore", "label": "Ability to restore access to personal data after an incident in a timely manner"},
            {"article": 32, "id": "art32_testing", "label": "Regular testing and evaluation of technical and organisational security measures"},
            {"article": 32, "id": "art32_access_control", "label": "Access control and authorisation procedures for personal data systems"},
        ],
    },
    "breach_response_plan": {
        "articles": [33, 34],
        "clauses": [
            {"article": 33, "id": "art33_72hr", "label": "72-hour notification procedure to supervisory authority"},
            {"article": 33, "id": "art33_content", "label": "Required notification content (nature of breach, categories affected, DPO contact, consequences, measures taken)"},
            {"article": 33, "id": "art33_documentation", "label": "Internal documentation of all breaches regardless of notification obligation"},
            {"article": 33, "id": "art33_risk_assessment", "label": "Risk assessment process to determine whether notification is required"},
            {"article": 34, "id": "art34_high_risk", "label": "Communication to affected individuals when processing poses high risk to their rights"},
            {"article": 34, "id": "art34_content", "label": "Required content of individual notification (nature, DPO contact, consequences, measures)"},
        ],
    },
    "dpia_template": {
        "articles": [35, 36],
        "clauses": [
            {"article": 35, "id": "art35_description", "label": "Systematic description of processing operations and purposes"},
            {"article": 35, "id": "art35_necessity", "label": "Assessment of necessity and proportionality of the processing"},
            {"article": 35, "id": "art35_risks", "label": "Assessment of risks to rights and freedoms of data subjects"},
            {"article": 35, "id": "art35_measures", "label": "Measures envisaged to address risks and demonstrate GDPR compliance"},
            {"article": 35, "id": "art35_dpo_consultation", "label": "DPO consultation and opinion recorded in the DPIA"},
            {"article": 36, "id": "art36_prior_consultation", "label": "Prior consultation with supervisory authority when residual risk remains high"},
        ],
    },
}

_STUB_NOTE = "AI evaluation not available. Configure Azure OpenAI credentials to enable document analysis."


# ── Result types ──────────────────────────────────────────────────────────────

@dataclass
class ClauseResult:
    article: int
    clause_id: str
    label: str
    status: str  # met | partial | not_met
    note: str = ""


@dataclass
class EvaluationResult:
    document_type: str
    articles_covered: list[int]
    clauses: list[ClauseResult]
    overall_status: str  # compliant | partial | non_compliant


# ── Evaluator ─────────────────────────────────────────────────────────────────

class EvidenceEvaluator:

    async def evaluate(self, document_type: str, text: str) -> EvaluationResult:
        spec = _DOCUMENT_SPECS.get(document_type)
        if not spec:
            raise ValueError(f"Unknown document type: {document_type}")
        if not settings.ai_enabled:
            return self._stub(document_type, spec)
        return await self._ai_evaluate(document_type, spec, text)

    async def _ai_evaluate(self, document_type: str, spec: dict, text: str) -> EvaluationResult:
        clause_list = "\n".join(
            f'{i + 1}. {c["id"]}: {c["label"]}' for i, c in enumerate(spec["clauses"])
        )
        prompt = f"""You are a GDPR compliance expert. Evaluate the following document against the GDPR compliance clauses listed below.

For each clause, determine if it is:
- "met": clearly and adequately addressed
- "partial": mentioned but incomplete or ambiguous
- "not_met": not addressed at all

Required clauses:
{clause_list}

Document text (first 12000 chars):
{text[:12000]}

Return ONLY a JSON object with this exact structure — no preamble, no markdown:
{{
  "clauses": [
    {{"id": "<id>", "status": "met|partial|not_met", "note": "<one sentence explanation>"}},
    ...
  ]
}}"""

        from common.ai.client import get_async_client
        client = get_async_client(settings)
        resp = await client.chat.completions.create(
            model=settings.azure_openai_deployment_gpt4o,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=2000,
        )
        raw = (resp.choices[0].message.content or "").strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        ai_result = json.loads(raw.strip())

        status_map = {c["id"]: c for c in ai_result.get("clauses", [])}
        clause_results = [
            ClauseResult(
                article=clause["article"],
                clause_id=clause["id"],
                label=clause["label"],
                status=status_map.get(clause["id"], {}).get("status", "not_met"),
                note=status_map.get(clause["id"], {}).get("note", ""),
            )
            for clause in spec["clauses"]
        ]
        return EvaluationResult(
            document_type=document_type,
            articles_covered=spec["articles"],
            clauses=clause_results,
            overall_status=self._overall_status(clause_results),
        )

    def _stub(self, document_type: str, spec: dict) -> EvaluationResult:
        clause_results = [
            ClauseResult(
                article=c["article"],
                clause_id=c["id"],
                label=c["label"],
                status="not_met",
                note=_STUB_NOTE,
            )
            for c in spec["clauses"]
        ]
        return EvaluationResult(
            document_type=document_type,
            articles_covered=spec["articles"],
            clauses=clause_results,
            overall_status="non_compliant",
        )

    def _overall_status(self, clauses: list[ClauseResult]) -> str:
        if not clauses:
            return "non_compliant"
        met = sum(1 for c in clauses if c.status == "met")
        if met == len(clauses):
            return "compliant"
        if met == 0 and all(c.status == "not_met" for c in clauses):
            return "non_compliant"
        return "partial"
