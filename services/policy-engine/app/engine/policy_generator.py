# WHAT: Policy generator engine | CHANGE: new file | WHY: COM-175 — drafts EU compliance policy documents from gaps + profile via Azure OpenAI, with stub fallback when AI is unavailable

from dataclasses import dataclass

from common.ai.client import get_async_client
from common.models.policy import PolicyType

from app.config import PolicySettings
from app.engine.policy_templates import POLICY_LABELS, get_sections


# ── Context dataclasses ──────────────────────────────────────────────────────

@dataclass
class GapContext:
    article: str | None
    title: str | None
    plain_english: str | None
    remediation_hint: str | None
    severity: str | None
    regulation_name: str | None


@dataclass
class ProfileContext:
    tenant_name: str
    industry: str | None
    company_size: str | None
    primary_jurisdiction: str | None
    dpo_name: str | None
    dpo_email: str | None
    legal_contact_email: str | None


# ── Prompt ────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = (
    "You are an EU data protection and compliance expert. You draft clear, "
    "legally-grounded compliance documents for small and medium businesses, "
    "in plain English, formatted as Markdown. Use square-bracket placeholders "
    "(e.g. [DATE], [ADDRESS], [SIGNATURE]) for information you don't have. "
    "Output only the Markdown document — no commentary, no code fences."
)


class PolicyGenerator:
    def __init__(self, settings: PolicySettings):
        self.settings = settings

    async def generate(
        self,
        policy_type: PolicyType,
        gaps: list[GapContext],
        profile: ProfileContext,
    ) -> tuple[str, bool]:
        """Returns (markdown_content, is_ai_enhanced)."""
        sections = get_sections(policy_type)

        if not self.settings.ai_enabled:
            return self._stub(policy_type, sections, gaps, profile), False

        try:
            content = await self._generate_ai(policy_type, sections, gaps, profile)
            return content, True
        except Exception:
            return self._stub(policy_type, sections, gaps, profile), False

    async def _generate_ai(
        self,
        policy_type: PolicyType,
        sections: list[tuple[str, str]],
        gaps: list[GapContext],
        profile: ProfileContext,
    ) -> str:
        client = get_async_client(self.settings)
        label = POLICY_LABELS.get(policy_type, policy_type.value.replace("_", " ").title())

        section_lines = "\n".join(
            f"{i}. **{title}** — {desc}" for i, (title, desc) in enumerate(sections, start=1)
        )
        gap_lines = "\n".join(
            f"- [{g.regulation_name or ''} {g.article or ''}] {g.title or ''}: {g.plain_english or ''} "
            f"(Severity: {g.severity or 'unknown'}). Remediation: {g.remediation_hint or 'n/a'}"
            for g in gaps
        ) or "- No specific gaps provided."

        user_prompt = f"""Company: {profile.tenant_name}
Industry: {profile.industry or "not specified"}
Company size: {profile.company_size or "not specified"}
Primary jurisdiction: {profile.primary_jurisdiction or "not specified"}
DPO / contact: {profile.dpo_name or "[DPO NAME]"} ({profile.dpo_email or profile.legal_contact_email or "[CONTACT EMAIL]"})

Compliance gaps this document should address:
{gap_lines}

Draft a {label} in Markdown. It MUST include the following sections, in this order, using level-2 headings (##):

{section_lines}

Tailor the content to the company details and gaps above. Use [DATE] for today's date and [SIGNATURE] for signature blocks. Output only the Markdown document."""

        response = await client.chat.completions.create(
            model=self.settings.azure_openai_deployment_gpt4o,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
        )
        return (response.choices[0].message.content or "").strip()

    def _stub(
        self,
        policy_type: PolicyType,
        sections: list[tuple[str, str]],
        gaps: list[GapContext],
        profile: ProfileContext,
    ) -> str:
        label = POLICY_LABELS.get(policy_type, policy_type.value.replace("_", " ").title())
        lines = [f"# {label}", "", f"**Company:** {profile.tenant_name}", "**Date:** [DATE]", ""]

        for title, desc in sections:
            lines.append(f"## {title}")
            lines.append("")
            lines.append(f"_{desc}_")
            lines.append("")
            lines.append("[TO BE COMPLETED]")
            lines.append("")

        gap_lines = "\n".join(
            f"- [{g.regulation_name or ''} {g.article or ''}] {g.title or ''}: "
            f"{g.remediation_hint or g.plain_english or ''}"
            for g in gaps
        )
        if gap_lines:
            lines.append("## Related Compliance Gaps")
            lines.append("")
            lines.append(gap_lines)
            lines.append("")

        return "\n".join(lines)
