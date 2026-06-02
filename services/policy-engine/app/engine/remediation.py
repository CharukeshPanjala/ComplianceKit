"""
COM-165 — Remediation Generator

Takes scoring results and generates prioritised action items for the tenant.
Converts raw gap data into actionable remediation guidance.

Priority order:
  1. not_met + critical severity  → fix immediately
  2. not_met + high severity      → fix urgently  
  3. unknown + critical/high      → gather data to evaluate
  4. partial + any severity       → improve existing controls
  5. not_met + medium/low         → fix when possible
  6. unknown + medium/low         → lower priority data gathering
"""
from dataclasses import dataclass
from common.models.rule import Rule, Severity
from app.engine.scorer import ScoringResult


# ── Result ────────────────────────────────────────────────────────────────────

@dataclass
class RemediationItem:
    rule: Rule
    status: str
    remediation_priority: str
    remediation_hint: str
    remediation_steps: list[str]
    remediation_resources: list[dict]
    evidence_needed: str | None   # for unknown rules — what we need from the tenant
    fine_exposure: str | None     # potential fine if not resolved


# ── Priority ordering ─────────────────────────────────────────────────────────

PRIORITY_ORDER = {
    ("not_met", Severity.CRITICAL): 1,
    ("not_met", Severity.HIGH): 2,
    ("unknown", Severity.CRITICAL): 3,
    ("unknown", Severity.HIGH): 4,
    ("partial", Severity.CRITICAL): 5,
    ("partial", Severity.HIGH): 6,
    ("not_met", Severity.MEDIUM): 7,
    ("unknown", Severity.MEDIUM): 8,
    ("partial", Severity.MEDIUM): 9,
    ("not_met", Severity.LOW): 10,
    ("unknown", Severity.LOW): 11,
    ("partial", Severity.LOW): 12,
}

FINE_EXPOSURE = {
    "tier_2": "Up to €20M or 4% of global annual turnover",
    "tier_1": "Up to €10M or 2% of global annual turnover",
    None: None,
}

# What evidence we need from tenants for unknown rules
EVIDENCE_NEEDED = {
    "policy_required": "Please confirm whether this policy exists in your organisation.",
    "document_required": "Please upload or confirm the existence of the required document.",
    "technical": "Please confirm whether this technical control is implemented.",
}


# ── Generator ─────────────────────────────────────────────────────────────────

class RemediationGenerator:

    def __init__(self, scoring_results: list[ScoringResult]):
        self.scoring_results = scoring_results

    def generate(self) -> list[RemediationItem]:
        """
        Generate prioritised remediation items for all non-met rules.
        Met rules are excluded — no action needed.
        """
        items = []

        for result in self.scoring_results:
            if result.status == "met":
                continue  # nothing to fix

            item = self._build_item(result)
            items.append(item)

        # Sort by priority
        return sorted(items, key=lambda x: self._priority_key(x))

    def _build_item(self, result: ScoringResult) -> RemediationItem:
        rule = result.rule

        # Pull remediation steps from rule (seeded data)
        steps_data = rule.remediation_steps or {}
        steps = steps_data.get("steps", [])

        # If no steps seeded, generate a generic one from hint
        if not steps and rule.remediation_hint:
            steps = [rule.remediation_hint]

        # Pull resources from rule
        resources_data = rule.remediation_resources or {}
        resources = resources_data.get("links", [])

        # Evidence needed for unknown rules
        evidence_needed = None
        if result.status == "unknown":
            evidence_needed = EVIDENCE_NEEDED.get(
                rule.check_type,
                "Please provide additional information to evaluate this requirement."
            )

        return RemediationItem(
            rule=rule,
            status=result.status,
            remediation_priority=result.remediation_priority or "medium",
            remediation_hint=rule.remediation_hint or "",
            remediation_steps=steps,
            remediation_resources=resources,
            evidence_needed=evidence_needed,
            fine_exposure=FINE_EXPOSURE.get(rule.fine_tier),
        )

    def _priority_key(self, item: RemediationItem) -> int:
        key = (item.status, item.rule.severity)
        return PRIORITY_ORDER.get(key, 99)

    def summary(self, items: list[RemediationItem]) -> dict:
        """Summary counts for the remediation roadmap."""
        by_priority = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        by_status = {"not_met": 0, "partial": 0, "unknown": 0}

        for item in items:
            priority = item.remediation_priority
            if priority in by_priority:
                by_priority[priority] += 1
            status = item.status
            if status in by_status:
                by_status[status] += 1

        return {
            "total_action_items": len(items),
            "by_priority": by_priority,
            "by_status": by_status,
            "immediate_action_required": by_priority["critical"] > 0,
        }