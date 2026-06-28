"""
COM-164 — Scorer

Evaluates each applicable rule against the company profile and assigns:
  - met          → company satisfies this requirement (score = 100)
  - partial       → partially satisfies (score = 50)
  - not_met       → clearly does not satisfy (score = 0)
  - unknown       → not enough profile data to evaluate (excluded from score)

Scoring weights by severity:
  critical = 4 points
  high     = 3 points
  medium   = 2 points
  low      = 1 point

Overall score = (earned points / total possible points) * 100
Only 'met', 'partial', 'not_met' rules count toward score.
'unknown' rules are shown as gaps but don't penalise the score yet.
"""
from dataclasses import dataclass
from common.models.rule import Rule, Severity
from app.engine.applicability import ApplicabilityResult


# ── Result ────────────────────────────────────────────────────────────────────

@dataclass
class ScoringResult:
    rule: Rule
    status: str          # met | partial | not_met | unknown
    score: int           # 0, 50, or 100
    evidence: dict       # what profile data was used to evaluate
    remediation_priority: str | None  # critical | high | medium | low


# ── Severity weights ──────────────────────────────────────────────────────────

SEVERITY_WEIGHTS = {
    Severity.CRITICAL: 4,
    Severity.HIGH: 3,
    Severity.MEDIUM: 2,
    Severity.LOW: 1,
}


# ── Engine ────────────────────────────────────────────────────────────────────

class Scorer:

    def __init__(self, profile: dict, applicability_results: list[ApplicabilityResult], regulation_name: str):
        self.profile = profile
        self.applicability_results = applicability_results
        self.regulation_name = regulation_name

        # Profile shortcuts
        self.gdpr = profile.get("gdpr_data") or {}
        self.nis2 = profile.get("nis2_data") or {}
        self.ai = profile.get("ai_act_data") or {}
        self.data_categories = set(profile.get("data_categories_processed") or [])
        self.data_role = profile.get("data_role") or "controller"
        self.has_compliance_officer = profile.get("has_compliance_officer")
        self.uses_cloud = profile.get("uses_cloud_services")
        self.certifications = set(profile.get("certifications") or [])

    # ── Main entry point ──────────────────────────────────────────────────────

    def evaluate(self) -> list[ScoringResult]:
        """Score all applicable rules."""
        results = []
        for ar in self.applicability_results:
            if not ar.is_applicable:
                continue
            result = self._score(ar.rule)
            results.append(result)
        return results

    def calculate_overall_score(self, scoring_results: list[ScoringResult]) -> dict:
        """
        Calculate overall compliance score (0-100) weighted by severity.
        Only met/partial/not_met rules count — unknown rules are excluded.
        """
        total_weight = 0
        earned_weight = 0
        counts = {"met": 0, "partial": 0, "not_met": 0, "unknown": 0}

        for result in scoring_results:
            counts[result.status] += 1
            if result.status == "unknown":
                continue  # excluded from score

            weight = SEVERITY_WEIGHTS.get(result.rule.severity, 1)
            total_weight += weight
            if result.status == "met":
                earned_weight += weight
            elif result.status == "partial":
                earned_weight += weight * 0.5

        score = round((earned_weight / total_weight) * 100) if total_weight > 0 else 0

        # Risk level from score
        if score >= 80:
            risk_level = "low"
        elif score >= 60:
            risk_level = "medium"
        elif score >= 40:
            risk_level = "high"
        else:
            risk_level = "critical"

        return {
            "score": score,
            "risk_level": risk_level,
            "total_rules": len(scoring_results),
            "met_rules": counts["met"],
            "partial_rules": counts["partial"],
            "not_met_rules": counts["not_met"],
            "unknown_rules": counts["unknown"],
            "applicable_rules": len(scoring_results),
        }

    # ── Score dispatcher ──────────────────────────────────────────────────────

    def _score(self, rule: Rule) -> ScoringResult:
        """Route to the right scoring logic based on check_type."""
        if rule.check_type == "profile_field":
            return self._score_profile_field(rule)

        # policy_required, document_required, technical
        # We don't have enough data yet — mark as unknown
        return ScoringResult(
            rule=rule,
            status="unknown",
            score=0,
            evidence={"reason": f"cannot_evaluate_{rule.check_type}_without_additional_data"},
            remediation_priority=self._remediation_priority(rule, "unknown"),
        )

    # ── Profile field scoring ─────────────────────────────────────────────────

    def _score_profile_field(self, rule: Rule) -> ScoringResult:
        """Route profile_field rules to the right regulation's scoring logic.

        Article numbers are not unique across regulations — each regulation
        restarts numbering near 1 — so this must dispatch by regulation_name
        before checking article_number, or rules from different regulations
        with the same number will collide.
        """
        if self.regulation_name == "GDPR":
            return self._score_gdpr_field(rule)
        if self.regulation_name == "NIS2":
            return self._score_nis2_field(rule)
        if self.regulation_name == "EU_AI_ACT":
            return self._score_ai_act_field(rule)
        return self._result(rule, "unknown", {"reason": "evaluation_logic_not_yet_implemented"})

    def _score_gdpr_field(self, rule: Rule) -> ScoringResult:
        n = rule.article_number

        # Art. 3 — Territorial scope
        if n == 3:
            jurisdiction = self.profile.get("primary_jurisdiction") or ""
            return self._result(rule, "met", {"primary_jurisdiction": jurisdiction})

        # Art. 6 — Lawfulness of processing
        if n == 6:
            lawful_bases = self.gdpr.get("lawful_bases") or []
            if lawful_bases:
                return self._result(rule, "met", {"lawful_bases": lawful_bases})
            return self._result(rule, "not_met", {"lawful_bases": []})

        # Art. 7 — Consent conditions
        if n == 7:
            # Applicability engine already ensures consent is in lawful bases
            return self._result(rule, "unknown", {"reason": "consent_mechanism_requires_verification"})

        # Art. 8 — Children's consent
        if n == 8:
            processes_children = self.gdpr.get("processes_children_data")
            if processes_children:
                return self._result(rule, "unknown", {"reason": "age_verification_requires_technical_check"})
            return self._result(rule, "met", {"processes_children_data": False})

        # Art. 9 — Special categories
        if n == 9:
            special_categories = self.data_categories.intersection({
                "health", "biometric", "genetic", "racial_ethnic",
                "political", "religious", "trade_union", "sexual_orientation",
            })
            if special_categories:
                # They process special category data — need explicit consent or exemption
                # We can't verify without more data
                return self._result(rule, "unknown", {
                    "special_categories_processed": list(special_categories),
                    "reason": "explicit_consent_or_exemption_requires_verification",
                })
            return self._result(rule, "met", {"special_categories": "none"})

        # Art. 10 — Criminal conviction data
        if n == 10:
            if "criminal_convictions" in self.data_categories:
                return self._result(rule, "unknown", {"reason": "legal_authority_requires_verification"})
            return self._result(rule, "met", {"criminal_conviction_data": False})

        # Art. 22 — Automated decisions
        if n == 22:
            uses_ai = self.ai.get("uses_ai")
            if uses_ai:
                return self._result(rule, "unknown", {"reason": "human_oversight_mechanism_requires_verification"})
            return self._result(rule, "met", {"uses_ai": False})

        # Art. 28 — Processor DPA
        if n == 28:
            uses_processors = self.gdpr.get("uses_data_processors")
            if uses_processors:
                return self._result(rule, "unknown", {"reason": "dpa_existence_requires_verification"})
            return self._result(rule, "met", {"uses_data_processors": False})

        # Arts. 33/34 — Breach notification procedure
        if n in {33, 34}:
            has_breach_procedure = self.gdpr.get("has_breach_procedure")
            if has_breach_procedure is True:
                return self._result(rule, "met", {"has_breach_procedure": True})
            if has_breach_procedure is False:
                return self._result(rule, "not_met", {"has_breach_procedure": False})
            return self._result(rule, "unknown", {"has_breach_procedure": None})

        # Arts. 35/36 — DPIA
        if n in {35, 36}:
            has_dpia = self.gdpr.get("has_dpia")
            if has_dpia is True:
                return self._result(rule, "met", {"has_dpia": True})
            if has_dpia is False:
                return self._result(rule, "not_met", {"has_dpia": False})
            return self._result(rule, "unknown", {"has_dpia": None})

        # Arts. 37/38/39 — DPO
        if n in {37, 38, 39}:
            has_dpo = self.has_compliance_officer
            if has_dpo is True:
                dpo_name = self.profile.get("dpo_name")
                dpo_email = self.profile.get("dpo_email")
                if dpo_name and dpo_email:
                    return self._result(rule, "met", {"has_compliance_officer": True})
                return self._result(rule, "partial", {"has_compliance_officer": True, "dpo_details_incomplete": True})
            if has_dpo is False:
                return self._result(rule, "unknown", {
                    "has_compliance_officer": False,
                    "reason": "dpo_mandatory_assessment_requires_verification",
                })
            return self._result(rule, "unknown", {"has_compliance_officer": None})

        # Arts. 44-49 — International transfers
        if n in {44, 45, 46, 47, 48, 49}:
            transfers = self.gdpr.get("transfers_outside_eea")
            transfer_mechanisms = self.gdpr.get("transfer_mechanisms") or []
            if transfers and not transfer_mechanisms:
                return self._result(rule, "not_met", {
                    "transfers_outside_eea": True,
                    "transfer_mechanisms": [],
                })
            if transfers and transfer_mechanisms:
                return self._result(rule, "met", {
                    "transfers_outside_eea": True,
                    "transfer_mechanisms": transfer_mechanisms,
                })
            return self._result(rule, "met", {"transfers_outside_eea": False})

        # Art. 27 — EU representative
        if n == 27:
            jurisdiction = self.profile.get("primary_jurisdiction") or ""
            return self._result(rule, "unknown", {
                "jurisdiction": jurisdiction,
                "reason": "eu_representative_appointment_requires_verification",
            })

        # Art. 19 — Notification to third parties (uses processors)
        if n == 19:
            uses_processors = self.gdpr.get("uses_data_processors")
            if uses_processors:
                return self._result(rule, "unknown", {"reason": "third_party_register_requires_verification"})
            return self._result(rule, "met", {"uses_data_processors": False})

        # Art. 20 — Data portability
        if n == 20:
            return self._result(rule, "unknown", {"reason": "portability_mechanism_requires_technical_verification"})

        # Default for GDPR profile_field rules we haven't explicitly handled
        return self._result(rule, "unknown", {"reason": "evaluation_logic_not_yet_implemented"})

    def _score_nis2_field(self, rule: Rule) -> ScoringResult:
        n = rule.article_number

        # NIS2 Art. 2/3 — Scope and entity type
        if n in {2, 3}:
            sectors = self.nis2.get("sectors") or []
            entity_type = self.nis2.get("entity_type") or ""
            if sectors and entity_type:
                return self._result(rule, "met", {"sectors": sectors, "entity_type": entity_type})
            return self._result(rule, "partial", {"sectors": sectors, "entity_type": entity_type})

        # NIS2 Arts. 18/23 — Incident reporting
        if n in {18, 23}:
            has_incident_plan = self.nis2.get("has_incident_response_plan")
            if has_incident_plan is True:
                return self._result(rule, "met", {"has_incident_response_plan": True})
            if has_incident_plan is False:
                return self._result(rule, "not_met", {"has_incident_response_plan": False})
            return self._result(rule, "unknown", {"has_incident_response_plan": None})

        # NIS2 Art. 27 — Registration
        if n == 27:
            return self._result(rule, "unknown", {"reason": "nis2_registration_requires_verification"})

        # Default for NIS2 profile_field rules we haven't explicitly handled
        return self._result(rule, "unknown", {"reason": "evaluation_logic_not_yet_implemented"})

    def _score_ai_act_field(self, rule: Rule) -> ScoringResult:
        n = rule.article_number

        # EU AI Act Art. 2 — Scope
        if n == 2:
            uses_ai = self.ai.get("uses_ai")
            role = self.ai.get("ai_role") or ""
            return self._result(rule, "met" if uses_ai and role else "partial", {
                "uses_ai": uses_ai,
                "ai_role": role,
            })

        # EU AI Act Art. 5 — Prohibited practices
        if n == 5:
            # We can't verify prohibited practices without detailed AI audit
            return self._result(rule, "unknown", {
                "reason": "prohibited_practices_require_ai_system_audit",
            })

        # EU AI Act Art. 6 — High-risk classification
        if n == 6:
            high_risk = self.ai.get("high_risk_ai_categories") or []
            return self._result(rule, "met" if high_risk is not None else "unknown", {
                "high_risk_ai_categories": high_risk,
            })

        # EU AI Act Art. 22 — Authorised representative (non-EU providers)
        if n == 22:
            jurisdiction = self.profile.get("primary_jurisdiction") or ""
            role = self.ai.get("ai_role") or ""
            if "provider" not in role and role != "both":
                return self._result(rule, "met", {"ai_role": role, "reason": "not_a_provider"})
            return self._result(rule, "unknown", {
                "primary_jurisdiction": jurisdiction,
                "reason": "eu_representative_appointment_requires_verification",
            })

        # EU AI Act Art. 26 — Deployer obligations
        if n == 26:
            role = self.ai.get("ai_role") or ""
            high_risk = self.ai.get("high_risk_ai_categories") or []
            if "deployer" in role or role == "both":
                if high_risk:
                    return self._result(rule, "unknown", {"reason": "deployer_obligations_require_verification"})
                return self._result(rule, "met", {"ai_role": role, "no_high_risk_ai": True})
            return self._result(rule, "met", {"deployer_obligations": "not_applicable"})

        # EU AI Act Art. 51 — GPAI systemic risk
        if n == 51:
            gpai = self.ai.get("uses_gpai")
            if gpai:
                return self._result(rule, "unknown", {"reason": "gpai_systemic_risk_requires_compute_verification"})
            return self._result(rule, "met", {"uses_gpai": False})

        # Default for AI Act profile_field rules we haven't explicitly handled
        return self._result(rule, "unknown", {"reason": "evaluation_logic_not_yet_implemented"})

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _result(self, rule: Rule, status: str, evidence: dict) -> ScoringResult:
        score_map = {"met": 100, "partial": 50, "not_met": 0, "unknown": 0}
        return ScoringResult(
            rule=rule,
            status=status,
            score=score_map.get(status, 0),
            evidence=evidence,
            remediation_priority=self._remediation_priority(rule, status),
        )

    def _remediation_priority(self, rule: Rule, status: str) -> str | None:
        """Priority is severity of the rule when not met or unknown."""
        if status == "met":
            return None
        severity_map = {
            Severity.CRITICAL: "critical",
            Severity.HIGH: "high",
            Severity.MEDIUM: "medium",
            Severity.LOW: "low",
        }
        return severity_map.get(rule.severity, "medium")