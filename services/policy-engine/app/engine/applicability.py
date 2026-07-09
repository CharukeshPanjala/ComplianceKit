"""
COM-163 — Applicability Engine

Determines which of the 258 rules apply to a company based on their profile.
Returns ApplicabilityResult for each rule — used by the scorer to evaluate gaps.

Rules are NOT applicable (excluded from scoring) if:
- check_type is 'informational' — awareness only, no company action needed
- B2B/B2C mismatch — rule doesn't apply to this company type
- Regulation-specific condition not met — e.g. no EU transfers → transfer rules don't apply
"""
from dataclasses import dataclass
from common.models.rule import Rule


# ── Result ────────────────────────────────────────────────────────────────────

@dataclass
class ApplicabilityResult:
    rule: Rule
    is_applicable: bool
    reason: str  # audit trail — why applicable or not


# ── Engine ────────────────────────────────────────────────────────────────────

class ApplicabilityEngine:

    # Special category data types that trigger Art. 9
    SPECIAL_CATEGORIES = {
        "health", "biometric", "genetic", "racial_ethnic",
        "political", "religious", "trade_union", "sexual_orientation",
    }

    # EU jurisdictions — used to determine if EU representative needed
    EU_JURISDICTIONS = {
        "eu", "germany", "france", "ireland", "netherlands", "spain",
        "italy", "sweden", "denmark", "finland", "belgium", "austria",
        "portugal", "poland", "czech republic", "romania", "hungary",
        "greece", "slovakia", "bulgaria", "croatia", "slovenia",
        "estonia", "latvia", "lithuania", "luxembourg", "malta", "cyprus",
    }

    # NIS2 company size threshold — micro/small are exempt
    NIS2_EXEMPT_SIZES = {"1-10", "11-50"}

    # NIS2 Art. 2(2) — these sectors apply regardless of company size
    NIS2_SIZE_INDEPENDENT_SECTORS = {"digital_infrastructure", "public_administration"}

    # NIS2 sectors that require domain name database (Art. 28)
    DNS_SECTORS = {"dns_services", "tld_registries", "domain_registration"}

    # EU AI Act article ranges
    HIGH_RISK_ARTICLES = set(range(8, 50))    # Arts. 8–49
    PROVIDER_ARTICLES = {16, 17, 18, 20, 21, 22, 23, 24, 25, 43, 44, 47, 48, 49}
    DEPLOYER_ARTICLES = {26, 27}
    GPAI_ARTICLES = set(range(51, 57))        # Arts. 51–56

    def __init__(self, profile: dict, rules: list[Rule], regulation_name: str):
        self.profile = profile
        self.rules = rules
        self.regulation_name = regulation_name

        # Profile shortcuts
        self.gdpr = profile.get("gdpr_data") or {}
        self.nis2 = profile.get("nis2_data") or {}
        self.ai = profile.get("ai_act_data") or {}
        self.b2b_or_b2c = profile.get("b2b_or_b2c") or "both"
        self.data_role = profile.get("data_role") or "controller"
        self.data_categories = set(profile.get("data_categories_processed") or [])
        self.company_size = profile.get("company_size") or ""
        self.jurisdiction = (profile.get("primary_jurisdiction") or "").lower()

    # ── Main entry point ──────────────────────────────────────────────────────

    def evaluate(self) -> list[ApplicabilityResult]:
        """Evaluate all rules and return applicability results."""
        return [
            ApplicabilityResult(
                rule=rule,
                is_applicable=applicable,
                reason=reason,
            )
            for rule in self.rules
            for applicable, reason in [self._check(rule)]
        ]

    # ── Universal filters ─────────────────────────────────────────────────────

    def _check(self, rule: Rule) -> tuple[bool, str]:
        # Informational rules — never scored, just awareness
        if rule.check_type == "informational":
            return False, "informational_only"

        # B2B/B2C mismatch
        if self.b2b_or_b2c == "b2b" and not rule.applies_to_b2b:
            return False, "not_applicable_to_b2b"
        if self.b2b_or_b2c == "b2c" and not rule.applies_to_b2c:
            return False, "not_applicable_to_b2c"

        # Route to regulation-specific logic
        if self.regulation_name == "GDPR":
            return self._check_gdpr(rule)
        if self.regulation_name == "NIS2":
            return self._check_nis2(rule)
        if self.regulation_name == "EU_AI_ACT":
            return self._check_ai_act(rule)

        return True, "applicable"

    # ── GDPR ──────────────────────────────────────────────────────────────────

    def _check_gdpr(self, rule: Rule) -> tuple[bool, str]:
        # GDPR section not completed in onboarding
        if not self.gdpr:
            return False, "gdpr_onboarding_incomplete"

        n = rule.article_number
        lawful_bases = set(self.gdpr.get("lawful_bases") or [])
        uses_processors = self.gdpr.get("uses_data_processors", False)
        transfers_outside_eea = self.gdpr.get("transfers_outside_eea", False)
        processes_children = self.gdpr.get("processes_children_data", False)
        is_processor_only = self.data_role == "processor"

        # Processor-only companies — skip controller-only obligations
        if is_processor_only and n in {
            13, 14,           # transparency to data subjects (controller duty)
            15, 16, 17, 18,   # data subject rights (controller duty)
            19, 20, 21, 22,   # more data subject rights
            24, 25, 26,       # controller responsibility, PbD, joint controllers
        }:
            return False, "controller_obligation_not_applicable_to_processors"

        # Consent-specific rules
        if n == 7 and "consent" not in lawful_bases:
            return False, "consent_not_used_as_lawful_basis"

        # Children's data
        if n == 8 and not processes_children:
            return False, "does_not_process_childrens_data"

        # Special category data (Art. 9)
        if n == 9 and not self.data_categories.intersection(self.SPECIAL_CATEGORIES):
            return False, "no_special_category_data_processed"

        # Criminal conviction data (Art. 10)
        if n == 10 and "criminal_convictions" not in self.data_categories:
            return False, "no_criminal_conviction_data_processed"

        # Data portability — only consent or contract
        if n == 20 and not lawful_bases.intersection({"consent", "contract"}):
            return False, "portability_only_applies_to_consent_or_contract"

        # Automated decisions — only if using AI
        if n == 22 and not self.ai.get("uses_ai"):
            return False, "does_not_use_ai_or_automated_decisions"

        # Processor obligations — only if using processors
        if n in {19, 28, 29} and not uses_processors:
            return False, "does_not_use_data_processors"

        # International transfers
        if n in {44, 45, 46, 47, 48, 49} and not transfers_outside_eea:
            return False, "no_transfers_outside_eea"

        # EU representative — only for non-EU establishments
        if n == 27:
            if any(eu in self.jurisdiction for eu in self.EU_JURISDICTIONS):
                return False, "established_in_eu_no_representative_needed"

        return True, "applicable"

    # ── NIS2 ──────────────────────────────────────────────────────────────────

    def _check_nis2(self, rule: Rule) -> tuple[bool, str]:
        # NIS2 section not completed
        if not self.nis2:
            return False, "nis2_onboarding_incomplete"

        sectors = set(self.nis2.get("sectors") or [])
        entity_type = self.nis2.get("entity_type") or ""
        n = rule.article_number

        # Not in any NIS2 covered sector
        if not sectors or sectors == {"not_applicable"}:
            return False, "not_in_nis2_covered_sector"

        # Micro/small companies are NIS2 exempt, unless they're in a sector
        # that's in scope regardless of size (Art. 2(2))
        if (
            self.company_size in self.NIS2_EXEMPT_SIZES
            and not sectors.intersection(self.NIS2_SIZE_INDEPENDENT_SECTORS)
        ):
            return False, "company_size_exempt_from_nis2"

        # Essential entity-specific proactive supervision
        if n == 32 and entity_type != "essential":
            return False, "proactive_supervision_only_for_essential_entities"

        # Important entity-specific reactive supervision
        if n == 33 and entity_type != "important":
            return False, "reactive_supervision_only_for_important_entities"

        # Domain name database — only for DNS/TLD providers
        if n == 28 and not sectors.intersection(self.DNS_SECTORS):
            return False, "domain_database_only_for_dns_tld_providers"

        return True, "applicable"

    # ── EU AI Act ─────────────────────────────────────────────────────────────

    def _check_ai_act(self, rule: Rule) -> tuple[bool, str]:
        # AI Act section not completed
        if not self.ai:
            return False, "ai_act_onboarding_incomplete"

        uses_ai = self.ai.get("uses_ai", False)
        role = self.ai.get("ai_role") or ""
        high_risk = self.ai.get("high_risk_ai_categories") or []
        gpai = self.ai.get("uses_gpai", False)
        n = rule.article_number

        # AI Act only applies if company uses AI
        if not uses_ai:
            return False, "does_not_use_ai"

        # High-risk AI requirements — only if operating high-risk AI
        if n in self.HIGH_RISK_ARTICLES and n not in {6, 7} and not high_risk:
            return False, "does_not_operate_high_risk_ai"

        # Provider-specific obligations
        if n in self.PROVIDER_ARTICLES:
            if role not in {"provider", "both"}:
                return False, "provider_obligations_not_applicable_to_deployers"

        # Deployer-specific obligations
        if n in self.DEPLOYER_ARTICLES:
            if role not in {"deployer", "both"}:
                return False, "deployer_obligations_not_applicable_to_providers"

        # GPAI model rules
        if n in self.GPAI_ARTICLES and not gpai:
            return False, "does_not_develop_gpai_models"

        # Importer obligations
        if n == 23 and "importer" not in role:
            return False, "importer_obligations_only_apply_to_importers"

        # EU representative — only for non-EU providers
        if n == 22:
            if any(eu in self.jurisdiction for eu in self.EU_JURISDICTIONS):
                return False, "established_in_eu_no_representative_needed"

        return True, "applicable"