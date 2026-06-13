# WHAT: Compliance report generator | CHANGE: new file | WHY: COM-177 — builds the markdown content for the one-click PDF/DOCX compliance report from assessments, gaps and the company profile

from dataclasses import dataclass
from datetime import datetime

from common.ai.client import get_async_client

from app.config import PolicySettings


# ── Labels ────────────────────────────────────────────────────────────────────

REGULATION_LABELS = {
    "GDPR": "GDPR",
    "NIS2": "NIS2",
    "EU_AI_ACT": "EU AI Act",
}

PRIORITY_ORDER = ["critical", "high", "medium", "low"]
PRIORITY_LABELS = {"critical": "Critical", "high": "High", "medium": "Medium", "low": "Low"}

STATUS_LABELS = {
    "met": "Met",
    "partial": "Partial",
    "not_met": "Not Met",
    "unknown": "Unknown",
}


# ── Context dataclasses ──────────────────────────────────────────────────────

@dataclass
class GapSummary:
    article: str | None
    title: str | None
    severity: str | None
    status: str
    remediation_priority: str | None
    remediation_hint: str | None
    resolved: bool


@dataclass
class RegulationSummary:
    regulation_name: str  # GDPR | NIS2 | EU_AI_ACT
    status: str  # assessment status value, or "never_run"
    score: int | None
    risk_level: str | None
    applicable_rules: int
    met_rules: int
    partial_rules: int
    not_met_rules: int
    unknown_rules: int
    completed_at: datetime | None
    gaps: list[GapSummary]


@dataclass
class ProfileSummary:
    tenant_name: str
    industry: str | None
    company_size: str | None
    b2b_or_b2c: str | None
    data_role: str | None
    primary_jurisdiction: str | None
    has_compliance_officer: bool | None
    dpo_name: str | None


# ── Prompt ────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = (
    "You are an EU data protection and compliance expert writing for company leadership "
    "and external auditors. Write a concise, professional executive summary in plain "
    "English, formatted as Markdown paragraphs (no headings, no bullet lists). "
    "Output exactly three paragraphs: (1) overall compliance posture and what the "
    "score means, (2) a brief regulation-by-regulation comparison highlighting "
    "strengths and weaknesses, (3) the most urgent priorities to address next. "
    "Be factual and specific, referencing the figures provided. Output only the "
    "Markdown paragraphs — no commentary, no code fences."
)


class ComplianceReportGenerator:
    def __init__(self, settings: PolicySettings):
        self.settings = settings

    async def generate_executive_summary(
        self,
        profile: ProfileSummary,
        regulations: list[RegulationSummary],
        overall_score: int,
    ) -> tuple[str, bool]:
        """Returns (markdown_text, is_ai_enhanced)."""
        if not self.settings.ai_enabled:
            return self._stub_summary(profile, regulations, overall_score), False

        try:
            text = await self._generate_ai_summary(profile, regulations, overall_score)
            return text, True
        except Exception:
            return self._stub_summary(profile, regulations, overall_score), False

    async def _generate_ai_summary(
        self,
        profile: ProfileSummary,
        regulations: list[RegulationSummary],
        overall_score: int,
    ) -> str:
        client = get_async_client(self.settings)

        reg_lines = []
        for r in regulations:
            label = REGULATION_LABELS.get(r.regulation_name, r.regulation_name)
            if r.status == "completed":
                reg_lines.append(
                    f"- {label}: score {r.score}%, risk level {r.risk_level or 'unknown'}, "
                    f"{r.met_rules} met / {r.partial_rules} partial / {r.not_met_rules} not met / "
                    f"{r.unknown_rules} unknown out of {r.applicable_rules} applicable rules"
                )
            else:
                reg_lines.append(f"- {label}: no completed assessment ({r.status})")

        critical_gaps = [
            f"- [{REGULATION_LABELS.get(r.regulation_name, r.regulation_name)} {g.article or ''}] {g.title or ''}"
            for r in regulations
            for g in r.gaps
            if g.remediation_priority == "critical" and not g.resolved
        ]

        user_prompt = f"""Company: {profile.tenant_name}
Industry: {profile.industry or "not specified"}
Overall compliance score: {overall_score}%

Regulation breakdown:
{chr(10).join(reg_lines)}

Top critical gaps:
{chr(10).join(critical_gaps) or "- None"}

Write the three-paragraph executive summary now."""

        response = await client.chat.completions.create(
            model=self.settings.azure_openai_deployment_gpt4o,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
        )
        return (response.choices[0].message.content or "").strip()

    def _stub_summary(
        self,
        profile: ProfileSummary,
        regulations: list[RegulationSummary],
        overall_score: int,
    ) -> str:
        completed = [r for r in regulations if r.status == "completed"]
        never_run = [r for r in regulations if r.status != "completed"]

        p1 = (
            f"{profile.tenant_name}'s overall compliance score is **{overall_score}%**, "
            f"based on {len(completed)} of {len(regulations)} regulation assessment(s) completed to date."
        )
        if never_run:
            names = ", ".join(REGULATION_LABELS.get(r.regulation_name, r.regulation_name) for r in never_run)
            p1 += f" {names} assessment(s) have not yet been run and are excluded from this score."

        reg_bits = [
            f"{REGULATION_LABELS.get(r.regulation_name, r.regulation_name)} scored {r.score}% "
            f"({(r.risk_level or 'unknown').title()} risk)"
            for r in completed
        ]
        p2 = (
            "Across the assessed regulations: " + "; ".join(reg_bits) + "."
            if reg_bits
            else "No regulation scores are available yet."
        )

        actionable = [
            (REGULATION_LABELS.get(r.regulation_name, r.regulation_name), g)
            for r in regulations
            for g in r.gaps
            if not g.resolved and g.remediation_priority == "critical"
        ]
        if actionable:
            items = "; ".join(f"{label} {g.article or ''} ({g.title or ''})" for label, g in actionable[:3])
            p3 = (
                f"The most urgent priorities are: {items}. Addressing these critical gaps first "
                f"will have the greatest impact on overall compliance posture."
            )
        else:
            p3 = (
                "There are no outstanding critical-priority gaps. Continue monitoring partial and "
                "unknown items to maintain and improve the current compliance posture."
            )

        return f"{p1}\n\n{p2}\n\n{p3}"

    def build_report_markdown(
        self,
        profile: ProfileSummary,
        regulations: list[RegulationSummary],
        overall_score: int,
        executive_summary: str,
    ) -> str:
        lines: list[str] = ["# Compliance Report", ""]

        lines += ["## Executive Summary", "", executive_summary, ""]

        lines += [
            "## Regulation Breakdown",
            "",
            "| Regulation | Status | Score | Risk Level | Applicable | Met | Partial | Not Met | Unknown |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
        for r in regulations:
            label = REGULATION_LABELS.get(r.regulation_name, r.regulation_name)
            status_str = r.status.replace("_", " ").title()
            if r.status == "completed":
                score_str = f"{r.score}%"
                risk_str = (r.risk_level or "—").title()
            else:
                score_str = "—"
                risk_str = "—"
            lines.append(
                f"| {label} | {status_str} | {score_str} | {risk_str} | "
                f"{r.applicable_rules} | {r.met_rules} | {r.partial_rules} | {r.not_met_rules} | {r.unknown_rules} |"
            )
        lines.append("")

        for r in regulations:
            label = REGULATION_LABELS.get(r.regulation_name, r.regulation_name)
            lines += [f"## Gap Analysis — {label}", ""]
            if r.status != "completed":
                lines += ["_No completed assessment for this regulation yet._", ""]
                continue
            if not r.gaps:
                lines += ["_No applicable rules found for this regulation._", ""]
                continue
            lines += [
                "| Article | Title | Severity | Status | Priority |",
                "| --- | --- | --- | --- | --- |",
            ]
            for g in r.gaps:
                lines.append(
                    f"| {g.article or '—'} | {g.title or '—'} | {(g.severity or '—').title()} | "
                    f"{STATUS_LABELS.get(g.status, g.status.title())} | "
                    f"{PRIORITY_LABELS.get(g.remediation_priority, '—')} |"
                )
            lines.append("")

        lines += ["## Remediation Roadmap", ""]
        actionable = [
            (REGULATION_LABELS.get(r.regulation_name, r.regulation_name), g)
            for r in regulations
            for g in r.gaps
            if not g.resolved and g.remediation_priority and g.status not in ("met", "not_applicable")
        ]
        if not actionable:
            lines += ["_No outstanding remediation items — all applicable gaps are met or resolved._", ""]
        else:
            for priority in PRIORITY_ORDER:
                items = [(label, g) for label, g in actionable if g.remediation_priority == priority]
                if not items:
                    continue
                lines += [f"### {PRIORITY_LABELS[priority]} Priority", ""]
                for label, g in items:
                    hint = g.remediation_hint or "Review and remediate."
                    lines.append(f"- **[{label} {g.article or ''}]** {g.title or ''} — {hint}")
                lines.append("")

        lines += ["## Profile Summary", ""]
        lines.append(f"- **Company:** {profile.tenant_name}")
        if profile.industry:
            lines.append(f"- **Industry:** {profile.industry.replace('_', ' ').title()}")
        if profile.company_size:
            lines.append(f"- **Company Size:** {profile.company_size}")
        if profile.b2b_or_b2c:
            lines.append(f"- **Business Model:** {profile.b2b_or_b2c.upper()}")
        if profile.data_role:
            lines.append(f"- **Data Role:** {profile.data_role.title()}")
        if profile.primary_jurisdiction:
            lines.append(f"- **Primary Jurisdiction:** {profile.primary_jurisdiction}")
        if profile.has_compliance_officer is not None:
            lines.append(f"- **Compliance Officer Appointed:** {'Yes' if profile.has_compliance_officer else 'No'}")
        if profile.dpo_name:
            lines.append(f"- **DPO:** {profile.dpo_name}")
        lines.append("")

        return "\n".join(lines)
