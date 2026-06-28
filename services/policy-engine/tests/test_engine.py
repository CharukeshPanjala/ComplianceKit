"""
COM-70 — Comprehensive tests for the assessment engine.
Covers applicability, scoring, and remediation including all edge cases.
"""
from unittest.mock import MagicMock
from common.models.rule import Rule, Severity
from app.engine.applicability import ApplicabilityEngine, ApplicabilityResult
from app.engine.scorer import Scorer, ScoringResult
from app.engine.remediation import RemediationGenerator


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_rule(**kwargs) -> Rule:
    rule = MagicMock(spec=Rule)
    rule.id = kwargs.get("id", "test-rule-id")
    rule.article_number = kwargs.get("article_number", 5)
    rule.article = kwargs.get("article", "Article 5")
    rule.check_type = kwargs.get("check_type", "profile_field")
    rule.applies_to_b2c = kwargs.get("applies_to_b2c", True)
    rule.applies_to_b2b = kwargs.get("applies_to_b2b", True)
    rule.severity = kwargs.get("severity", Severity.MEDIUM)
    rule.fine_tier = kwargs.get("fine_tier", None)
    rule.remediation_hint = kwargs.get("remediation_hint", "Fix this.")
    rule.remediation_steps = kwargs.get("remediation_steps", {"steps": ["Step 1"]})
    rule.remediation_resources = kwargs.get("remediation_resources", {"links": []})
    rule.is_mandatory = kwargs.get("is_mandatory", True)
    rule.profile_field = kwargs.get("profile_field", None)
    rule.regulation_name = kwargs.get("regulation_name", "GDPR")
    return rule


def make_profile(**kwargs) -> dict:
    """Build a complete company profile with sensible defaults."""
    return {
        "b2b_or_b2c": kwargs.get("b2b_or_b2c", "both"),
        "data_role": kwargs.get("data_role", "controller"),
        "company_size": kwargs.get("company_size", "51-200"),
        "primary_jurisdiction": kwargs.get("primary_jurisdiction", "Ireland"),
        "data_categories_processed": kwargs.get("data_categories_processed", ["email", "name"]),
        "has_compliance_officer": kwargs.get("has_compliance_officer", True),
        "dpo_name": kwargs.get("dpo_name", "Jane Smith"),
        "dpo_email": kwargs.get("dpo_email", "dpo@example.com"),
        "gdpr_data": kwargs.get("gdpr_data", {
            "lawful_bases": ["consent", "contract"],
            "processes_children_data": False,
            "transfers_outside_eea": False,
            "transfer_mechanisms": [],
            "uses_data_processors": True,
            "has_breach_procedure": True,
            "has_dpia": True,
        }),
        "nis2_data": kwargs.get("nis2_data", {}),
        "ai_act_data": kwargs.get("ai_act_data", {}),
    }


def make_applicability_result(rule, is_applicable=True, reason="applicable") -> ApplicabilityResult:
    return ApplicabilityResult(rule=rule, is_applicable=is_applicable, reason=reason)


def make_scoring_result(rule, status="not_met", priority="high") -> ScoringResult:
    score_map = {"met": 100, "partial": 50, "not_met": 0, "unknown": 0}
    return ScoringResult(
        rule=rule,
        status=status,
        score=score_map[status],
        evidence={},
        remediation_priority=None if status == "met" else priority,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# APPLICABILITY ENGINE TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestApplicabilityUniversalFilters:
    """Tests for filters that apply across all regulations."""

    def test_informational_always_not_applicable(self):
        """Informational rules never count toward score regardless of profile."""
        rule = make_rule(check_type="informational")
        engine = ApplicabilityEngine(make_profile(), [rule], "GDPR")
        results = engine.evaluate()
        assert results[0].is_applicable is False
        assert results[0].reason == "informational_only"

    def test_informational_not_applicable_even_in_nis2(self):
        """Informational filter works for NIS2 too."""
        rule = make_rule(check_type="informational")
        profile = make_profile(
            company_size="51-200",
            nis2_data={"sectors": ["energy"], "entity_type": "essential"}
        )
        engine = ApplicabilityEngine(profile, [rule], "NIS2")
        results = engine.evaluate()
        assert results[0].is_applicable is False
        assert results[0].reason == "informational_only"

    def test_b2b_company_skips_b2c_only_rule(self):
        """B2B-only company skips rules where applies_to_b2b=False."""
        rule = make_rule(applies_to_b2b=False, applies_to_b2c=True)
        engine = ApplicabilityEngine(make_profile(b2b_or_b2c="b2b"), [rule], "GDPR")
        results = engine.evaluate()
        assert results[0].is_applicable is False
        assert results[0].reason == "not_applicable_to_b2b"

    def test_b2c_company_skips_b2b_only_rule(self):
        """B2C-only company skips rules where applies_to_b2c=False."""
        rule = make_rule(applies_to_b2c=False, applies_to_b2b=True)
        engine = ApplicabilityEngine(make_profile(b2b_or_b2c="b2c"), [rule], "GDPR")
        results = engine.evaluate()
        assert results[0].is_applicable is False
        assert results[0].reason == "not_applicable_to_b2c"

    def test_both_company_applies_all_b2b_b2c_rules(self):
        """B2B+B2C company applies both B2B-only and B2C-only rules."""
        b2b_rule = make_rule(applies_to_b2b=True, applies_to_b2c=False)
        b2c_rule = make_rule(applies_to_b2c=True, applies_to_b2b=False)
        engine = ApplicabilityEngine(make_profile(b2b_or_b2c="both"), [b2b_rule, b2c_rule], "GDPR")
        results = engine.evaluate()
        assert results[0].is_applicable is True
        assert results[1].is_applicable is True

    def test_empty_rules_list_returns_empty_results(self):
        """Empty rules list produces empty results."""
        engine = ApplicabilityEngine(make_profile(), [], "GDPR")
        results = engine.evaluate()
        assert results == []


class TestApplicabilityGDPR:
    """Tests for GDPR-specific applicability logic."""

    def test_all_gdpr_rules_skipped_when_gdpr_data_empty(self):
        """All GDPR rules skip if gdpr_data is empty dict."""
        rule = make_rule(check_type="policy_required", article_number=5)
        engine = ApplicabilityEngine(make_profile(gdpr_data={}), [rule], "GDPR")
        assert engine.evaluate()[0].reason == "gdpr_onboarding_incomplete"

    def test_all_gdpr_rules_skipped_when_gdpr_data_none(self):
        """All GDPR rules skip if gdpr_data is None."""
        rule = make_rule(check_type="policy_required", article_number=5)
        engine = ApplicabilityEngine(make_profile(gdpr_data=None), [rule], "GDPR")
        assert engine.evaluate()[0].reason == "gdpr_onboarding_incomplete"

    def test_art7_not_applicable_without_consent_basis(self):
        """Art. 7 skipped when consent is not in lawful bases."""
        rule = make_rule(article_number=7, check_type="profile_field")
        profile = make_profile(gdpr_data={
            "lawful_bases": ["contract", "legal_obligation"],
            "processes_children_data": False,
            "transfers_outside_eea": False,
            "uses_data_processors": False,
            "has_breach_procedure": True,
            "has_dpia": True,
        })
        engine = ApplicabilityEngine(profile, [rule], "GDPR")
        assert engine.evaluate()[0].reason == "consent_not_used_as_lawful_basis"

    def test_art7_applicable_with_consent_basis(self):
        """Art. 7 applicable when consent is in lawful bases."""
        rule = make_rule(article_number=7, check_type="profile_field")
        engine = ApplicabilityEngine(make_profile(), [rule], "GDPR")
        assert engine.evaluate()[0].is_applicable is True

    def test_art8_not_applicable_without_children_data(self):
        """Art. 8 skipped when not processing children's data."""
        rule = make_rule(article_number=8, check_type="profile_field")
        engine = ApplicabilityEngine(make_profile(), [rule], "GDPR")
        result = engine.evaluate()[0]
        assert result.is_applicable is False
        assert result.reason == "does_not_process_childrens_data"

    def test_art8_applicable_with_children_data(self):
        """Art. 8 applicable when processing children's data."""
        rule = make_rule(article_number=8, check_type="profile_field")
        profile = make_profile(gdpr_data={
            "lawful_bases": ["consent"],
            "processes_children_data": True,
            "transfers_outside_eea": False,
            "uses_data_processors": False,
            "has_breach_procedure": True,
            "has_dpia": True,
        })
        engine = ApplicabilityEngine(profile, [rule], "GDPR")
        assert engine.evaluate()[0].is_applicable is True

    def test_art9_not_applicable_without_special_data(self):
        """Art. 9 skipped when no special category data processed."""
        rule = make_rule(article_number=9, check_type="profile_field")
        engine = ApplicabilityEngine(
            make_profile(data_categories_processed=["email", "name"]), [rule], "GDPR"
        )
        assert engine.evaluate()[0].reason == "no_special_category_data_processed"

    def test_art9_applicable_with_health_data(self):
        """Art. 9 applicable when health data is processed."""
        rule = make_rule(article_number=9, check_type="profile_field")
        engine = ApplicabilityEngine(
            make_profile(data_categories_processed=["email", "health"]), [rule], "GDPR"
        )
        assert engine.evaluate()[0].is_applicable is True

    def test_art9_applicable_with_biometric_data(self):
        """Art. 9 applicable when biometric data is processed."""
        rule = make_rule(article_number=9, check_type="profile_field")
        engine = ApplicabilityEngine(
            make_profile(data_categories_processed=["biometric"]), [rule], "GDPR"
        )
        assert engine.evaluate()[0].is_applicable is True

    def test_art9_applicable_with_any_special_category(self):
        """Art. 9 applicable for any of the 8 special categories."""
        special_cats = ["health", "biometric", "genetic", "racial_ethnic",
                       "political", "religious", "trade_union", "sexual_orientation"]
        rule = make_rule(article_number=9, check_type="profile_field")
        for cat in special_cats:
            engine = ApplicabilityEngine(
                make_profile(data_categories_processed=[cat]), [rule], "GDPR"
            )
            assert engine.evaluate()[0].is_applicable is True, f"Failed for {cat}"

    def test_art10_not_applicable_without_criminal_data(self):
        """Art. 10 skipped when no criminal conviction data."""
        rule = make_rule(article_number=10, check_type="profile_field")
        engine = ApplicabilityEngine(
            make_profile(data_categories_processed=["email"]), [rule], "GDPR"
        )
        assert engine.evaluate()[0].reason == "no_criminal_conviction_data_processed"

    def test_art10_applicable_with_criminal_data(self):
        """Art. 10 applicable when criminal conviction data processed."""
        rule = make_rule(article_number=10, check_type="profile_field")
        engine = ApplicabilityEngine(
            make_profile(data_categories_processed=["criminal_convictions"]), [rule], "GDPR"
        )
        assert engine.evaluate()[0].is_applicable is True

    def test_art20_not_applicable_without_portability_basis(self):
        """Art. 20 skipped when lawful basis is neither consent nor contract."""
        rule = make_rule(article_number=20, check_type="profile_field")
        profile = make_profile(gdpr_data={
            "lawful_bases": ["legal_obligation", "legitimate_interests"],
            "processes_children_data": False,
            "transfers_outside_eea": False,
            "uses_data_processors": False,
            "has_breach_procedure": True,
            "has_dpia": True,
        })
        engine = ApplicabilityEngine(profile, [rule], "GDPR")
        assert engine.evaluate()[0].reason == "portability_only_applies_to_consent_or_contract"

    def test_art20_applicable_with_consent_basis(self):
        """Art. 20 applicable when consent is lawful basis."""
        rule = make_rule(article_number=20, check_type="profile_field")
        engine = ApplicabilityEngine(make_profile(), [rule], "GDPR")
        assert engine.evaluate()[0].is_applicable is True

    def test_art20_applicable_with_contract_basis(self):
        """Art. 20 applicable when contract is lawful basis."""
        rule = make_rule(article_number=20, check_type="profile_field")
        profile = make_profile(gdpr_data={
            "lawful_bases": ["contract"],
            "processes_children_data": False,
            "transfers_outside_eea": False,
            "uses_data_processors": False,
            "has_breach_procedure": True,
            "has_dpia": True,
        })
        engine = ApplicabilityEngine(profile, [rule], "GDPR")
        assert engine.evaluate()[0].is_applicable is True

    def test_art22_not_applicable_without_ai(self):
        """Art. 22 (automated decisions) skipped when not using AI."""
        rule = make_rule(article_number=22, check_type="profile_field")
        engine = ApplicabilityEngine(make_profile(ai_act_data={}), [rule], "GDPR")
        assert engine.evaluate()[0].reason == "does_not_use_ai_or_automated_decisions"

    def test_art22_applicable_with_ai(self):
        """Art. 22 applicable when company uses AI."""
        rule = make_rule(article_number=22, check_type="profile_field")
        profile = make_profile(ai_act_data={"uses_ai": True, "ai_role": "deployer"})
        engine = ApplicabilityEngine(profile, [rule], "GDPR")
        assert engine.evaluate()[0].is_applicable is True

    def test_arts28_29_19_not_applicable_without_processors(self):
        """Arts. 19, 28, 29 skipped when no data processors used."""
        for article_num in [19, 28, 29]:
            rule = make_rule(article_number=article_num, check_type="document_required")
            profile = make_profile(gdpr_data={
                "lawful_bases": ["consent"],
                "processes_children_data": False,
                "transfers_outside_eea": False,
                "uses_data_processors": False,
                "has_breach_procedure": True,
                "has_dpia": True,
            })
            engine = ApplicabilityEngine(profile, [rule], "GDPR")
            assert engine.evaluate()[0].reason == "does_not_use_data_processors", \
                f"Art. {article_num} should not apply without processors"

    def test_arts28_29_19_applicable_with_processors(self):
        """Arts. 19, 28, 29 applicable when processors are used."""
        for article_num in [19, 28, 29]:
            rule = make_rule(article_number=article_num, check_type="document_required")
            engine = ApplicabilityEngine(make_profile(), [rule], "GDPR")
            assert engine.evaluate()[0].is_applicable is True, \
                f"Art. {article_num} should apply with processors"

    def test_transfer_articles_not_applicable_without_eea_transfers(self):
        """Arts. 44-49 all skipped when no transfers outside EEA."""
        for article_num in [44, 45, 46, 47, 48, 49]:
            rule = make_rule(article_number=article_num, check_type="policy_required")
            profile = make_profile(gdpr_data={
                "lawful_bases": ["consent"],
                "processes_children_data": False,
                "transfers_outside_eea": False,
                "uses_data_processors": False,
                "has_breach_procedure": True,
                "has_dpia": True,
            })
            engine = ApplicabilityEngine(profile, [rule], "GDPR")
            assert engine.evaluate()[0].reason == "no_transfers_outside_eea", \
                f"Art. {article_num} should not apply without EEA transfers"

    def test_transfer_articles_applicable_with_eea_transfers(self):
        """Arts. 44-49 all applicable when transfers outside EEA."""
        for article_num in [44, 45, 46, 47, 48, 49]:
            rule = make_rule(article_number=article_num, check_type="policy_required")
            profile = make_profile(gdpr_data={
                "lawful_bases": ["consent"],
                "processes_children_data": False,
                "transfers_outside_eea": True,
                "transfer_mechanisms": ["SCCs"],
                "uses_data_processors": False,
                "has_breach_procedure": True,
                "has_dpia": True,
            })
            engine = ApplicabilityEngine(profile, [rule], "GDPR")
            assert engine.evaluate()[0].is_applicable is True, \
                f"Art. {article_num} should apply with EEA transfers"

    def test_art27_not_applicable_for_eu_company(self):
        """Art. 27 (EU representative) not applicable when established in EU."""
        rule = make_rule(article_number=27, check_type="policy_required")
        eu_jurisdictions = ["Ireland", "Germany", "France", "Netherlands",
                           "Spain", "Italy", "Poland", "Sweden", "Belgium"]
        for jurisdiction in eu_jurisdictions:
            engine = ApplicabilityEngine(
                make_profile(primary_jurisdiction=jurisdiction), [rule], "GDPR"
            )
            result = engine.evaluate()[0]
            assert result.is_applicable is False, \
                f"Art. 27 should not apply for {jurisdiction}"
            assert result.reason == "established_in_eu_no_representative_needed"

    def test_art27_applicable_for_non_eu_company(self):
        """Art. 27 applicable when not established in EU."""
        rule = make_rule(article_number=27, check_type="policy_required")
        non_eu = ["United States", "Canada", "Australia", "Japan", "Brazil", "India"]
        for jurisdiction in non_eu:
            engine = ApplicabilityEngine(
                make_profile(primary_jurisdiction=jurisdiction), [rule], "GDPR"
            )
            result = engine.evaluate()[0]
            assert result.is_applicable is True, \
                f"Art. 27 should apply for {jurisdiction}"

    def test_processor_only_skips_controller_obligations(self):
        """Processor-only companies skip Arts. 13-26 (controller duties)."""
        controller_only_arts = {13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 24, 25, 26}
        for article_num in controller_only_arts:
            rule = make_rule(article_number=article_num, check_type="policy_required")
            engine = ApplicabilityEngine(
                make_profile(data_role="processor"), [rule], "GDPR"
            )
            result = engine.evaluate()[0]
            assert result.is_applicable is False, \
                f"Art. {article_num} should not apply to processor-only"
            assert result.reason == "controller_obligation_not_applicable_to_processors"

    def test_data_role_both_applies_all_obligations(self):
        """data_role='both' applies controller AND processor obligations."""
        rule = make_rule(article_number=13, check_type="policy_required")
        engine = ApplicabilityEngine(
            make_profile(data_role="both"), [rule], "GDPR"
        )
        assert engine.evaluate()[0].is_applicable is True

    def test_data_role_controller_applies_all_controller_obligations(self):
        """data_role='controller' applies all controller obligations."""
        rule = make_rule(article_number=13, check_type="policy_required")
        engine = ApplicabilityEngine(
            make_profile(data_role="controller"), [rule], "GDPR"
        )
        assert engine.evaluate()[0].is_applicable is True


class TestApplicabilityNIS2:
    """Tests for NIS2-specific applicability logic."""

    def _nis2_profile(self, **kwargs):
        return make_profile(
            company_size=kwargs.get("company_size", "51-200"),
            nis2_data=kwargs.get("nis2_data", {
                "sectors": ["energy"],
                "entity_type": "important"
            })
        )

    def test_all_nis2_skipped_when_no_sectors(self):
        """All NIS2 rules skipped when not in any covered sector."""
        rule = make_rule(article_number=21, check_type="technical")
        profile = self._nis2_profile(nis2_data={"sectors": [], "entity_type": ""})
        engine = ApplicabilityEngine(profile, [rule], "NIS2")
        assert engine.evaluate()[0].reason == "not_in_nis2_covered_sector"

    def test_all_nis2_skipped_when_nis2_data_empty(self):
        """All NIS2 rules skipped when nis2_data is empty."""
        rule = make_rule(article_number=21, check_type="technical")
        engine = ApplicabilityEngine(make_profile(nis2_data={}), [rule], "NIS2")
        assert engine.evaluate()[0].reason == "nis2_onboarding_incomplete"

    def test_all_nis2_skipped_when_nis2_data_none(self):
        """All NIS2 rules skipped when nis2_data is None."""
        rule = make_rule(article_number=21, check_type="technical")
        engine = ApplicabilityEngine(make_profile(nis2_data=None), [rule], "NIS2")
        assert engine.evaluate()[0].reason == "nis2_onboarding_incomplete"

    def test_micro_company_exempt_from_nis2(self):
        """1-10 employee companies are NIS2 exempt."""
        rule = make_rule(article_number=21, check_type="technical")
        profile = self._nis2_profile(company_size="1-10")
        engine = ApplicabilityEngine(profile, [rule], "NIS2")
        assert engine.evaluate()[0].reason == "company_size_exempt_from_nis2"

    def test_small_company_exempt_from_nis2(self):
        """11-50 employee companies are NIS2 exempt."""
        rule = make_rule(article_number=21, check_type="technical")
        profile = self._nis2_profile(company_size="11-50")
        engine = ApplicabilityEngine(profile, [rule], "NIS2")
        assert engine.evaluate()[0].reason == "company_size_exempt_from_nis2"

    def test_small_company_in_digital_infrastructure_not_exempt(self):
        """11-50 employee companies in digital_infrastructure are size-independent."""
        rule = make_rule(article_number=21, check_type="technical")
        profile = self._nis2_profile(
            company_size="11-50",
            nis2_data={"sectors": ["digital_infrastructure"], "entity_type": "important"},
        )
        engine = ApplicabilityEngine(profile, [rule], "NIS2")
        assert engine.evaluate()[0].is_applicable is True

    def test_small_company_in_public_administration_not_exempt(self):
        """11-50 employee public administration entities are size-independent."""
        rule = make_rule(article_number=21, check_type="technical")
        profile = self._nis2_profile(
            company_size="1-10",
            nis2_data={"sectors": ["public_administration"], "entity_type": "important"},
        )
        engine = ApplicabilityEngine(profile, [rule], "NIS2")
        assert engine.evaluate()[0].is_applicable is True

    def test_small_company_in_managed_services_still_exempt(self):
        """11-50 employee managed service providers still follow the size cap."""
        rule = make_rule(article_number=21, check_type="technical")
        profile = self._nis2_profile(
            company_size="11-50",
            nis2_data={"sectors": ["managed_services"], "entity_type": "important"},
        )
        engine = ApplicabilityEngine(profile, [rule], "NIS2")
        assert engine.evaluate()[0].reason == "company_size_exempt_from_nis2"

    def test_medium_company_in_scope_for_nis2(self):
        """51-200 employee companies are in NIS2 scope."""
        rule = make_rule(article_number=21, check_type="technical")
        profile = self._nis2_profile(company_size="51-200")
        engine = ApplicabilityEngine(profile, [rule], "NIS2")
        assert engine.evaluate()[0].is_applicable is True

    def test_large_company_in_scope_for_nis2(self):
        """201-1000 employee companies are in NIS2 scope."""
        rule = make_rule(article_number=21, check_type="technical")
        profile = self._nis2_profile(company_size="201-1000")
        engine = ApplicabilityEngine(profile, [rule], "NIS2")
        assert engine.evaluate()[0].is_applicable is True

    def test_very_large_company_in_scope_for_nis2(self):
        """1000+ employee companies are in NIS2 scope."""
        rule = make_rule(article_number=21, check_type="technical")
        profile = self._nis2_profile(company_size="1000+")
        engine = ApplicabilityEngine(profile, [rule], "NIS2")
        assert engine.evaluate()[0].is_applicable is True

    def test_art32_proactive_supervision_only_for_essential(self):
        """Art. 32 only applies to essential entities."""
        rule = make_rule(article_number=32, check_type="informational")
        profile = self._nis2_profile(
            nis2_data={"sectors": ["energy"], "entity_type": "important"}
        )
        engine = ApplicabilityEngine(profile, [rule], "NIS2")
        # informational is caught first
        assert engine.evaluate()[0].is_applicable is False

    def test_art32_applicable_for_essential_entity(self):
        """Art. 32 applicable for essential entities (non-informational version)."""
        rule = make_rule(article_number=32, check_type="policy_required")
        profile = self._nis2_profile(
            nis2_data={"sectors": ["energy"], "entity_type": "essential"}
        )
        engine = ApplicabilityEngine(profile, [rule], "NIS2")
        assert engine.evaluate()[0].is_applicable is True

    def test_art32_not_applicable_for_important_entity(self):
        """Art. 32 (proactive supervision) not applicable to important entities."""
        rule = make_rule(article_number=32, check_type="policy_required")
        profile = self._nis2_profile(
            nis2_data={"sectors": ["energy"], "entity_type": "important"}
        )
        engine = ApplicabilityEngine(profile, [rule], "NIS2")
        assert engine.evaluate()[0].reason == "proactive_supervision_only_for_essential_entities"

    def test_art33_not_applicable_for_essential_entity(self):
        """Art. 33 (reactive supervision) not applicable to essential entities."""
        rule = make_rule(article_number=33, check_type="policy_required")
        profile = self._nis2_profile(
            nis2_data={"sectors": ["energy"], "entity_type": "essential"}
        )
        engine = ApplicabilityEngine(profile, [rule], "NIS2")
        assert engine.evaluate()[0].reason == "reactive_supervision_only_for_important_entities"

    def test_art33_applicable_for_important_entity(self):
        """Art. 33 (reactive supervision) applicable to important entities."""
        rule = make_rule(article_number=33, check_type="policy_required")
        profile = self._nis2_profile(
            nis2_data={"sectors": ["energy"], "entity_type": "important"}
        )
        engine = ApplicabilityEngine(profile, [rule], "NIS2")
        assert engine.evaluate()[0].is_applicable is True

    def test_art28_domain_database_not_applicable_for_non_dns(self):
        """Art. 28 not applicable for non-DNS sectors."""
        rule = make_rule(article_number=28, check_type="policy_required")
        profile = self._nis2_profile(
            nis2_data={"sectors": ["energy", "transport"], "entity_type": "essential"}
        )
        engine = ApplicabilityEngine(profile, [rule], "NIS2")
        assert engine.evaluate()[0].reason == "domain_database_only_for_dns_tld_providers"

    def test_art28_applicable_for_dns_sector(self):
        """Art. 28 applicable for DNS service providers."""
        rule = make_rule(article_number=28, check_type="policy_required")
        profile = self._nis2_profile(
            nis2_data={"sectors": ["dns_services"], "entity_type": "essential"}
        )
        engine = ApplicabilityEngine(profile, [rule], "NIS2")
        assert engine.evaluate()[0].is_applicable is True


class TestApplicabilityAIAct:
    """Tests for EU AI Act-specific applicability logic."""

    def _ai_profile(self, **kwargs):
        return make_profile(ai_act_data=kwargs.get("ai_act_data", {
            "uses_ai": True,
            "ai_role": "provider",
            "high_risk_ai_categories": ["employment"],
            "uses_gpai": False,
        }))

    def test_all_ai_act_skipped_when_no_ai(self):
        """All AI Act rules skipped when company doesn't use AI."""
        rule = make_rule(article_number=5, check_type="profile_field")
        engine = ApplicabilityEngine(
            make_profile(ai_act_data={"uses_ai": False}), [rule], "EU_AI_ACT"
        )
        assert engine.evaluate()[0].reason == "does_not_use_ai"

    def test_all_ai_act_skipped_when_ai_data_empty(self):
        """All AI Act rules skipped when ai_act_data is empty."""
        rule = make_rule(article_number=5, check_type="profile_field")
        engine = ApplicabilityEngine(make_profile(ai_act_data={}), [rule], "EU_AI_ACT")
        assert engine.evaluate()[0].reason == "ai_act_onboarding_incomplete"

    def test_all_ai_act_skipped_when_ai_data_none(self):
        """All AI Act rules skipped when ai_act_data is None."""
        rule = make_rule(article_number=5, check_type="profile_field")
        engine = ApplicabilityEngine(make_profile(ai_act_data=None), [rule], "EU_AI_ACT")
        assert engine.evaluate()[0].reason == "ai_act_onboarding_incomplete"

    def test_art5_always_applicable_if_uses_ai(self):
        """Art. 5 (prohibited practices) always applicable when company uses AI."""
        rule = make_rule(article_number=5, check_type="profile_field")
        engine = ApplicabilityEngine(self._ai_profile(), [rule], "EU_AI_ACT")
        assert engine.evaluate()[0].is_applicable is True

    def test_art6_always_applicable_if_uses_ai(self):
        """Art. 6 (classification) always applicable — excluded from high-risk filter."""
        rule = make_rule(article_number=6, check_type="profile_field")
        profile = make_profile(ai_act_data={
            "uses_ai": True, "ai_role": "deployer",
            "high_risk_ai_categories": [], "uses_gpai": False
        })
        engine = ApplicabilityEngine(profile, [rule], "EU_AI_ACT")
        assert engine.evaluate()[0].is_applicable is True

    def test_art7_always_applicable_if_uses_ai(self):
        """Art. 7 (classification amendments) always applicable."""
        rule = make_rule(article_number=7, check_type="profile_field")
        profile = make_profile(ai_act_data={
            "uses_ai": True, "ai_role": "deployer",
            "high_risk_ai_categories": [], "uses_gpai": False
        })
        engine = ApplicabilityEngine(profile, [rule], "EU_AI_ACT")
        assert engine.evaluate()[0].is_applicable is True

    def test_high_risk_articles_not_applicable_without_high_risk_ai(self):
        """Arts. 8-49 (except 6,7) not applicable without high-risk categories."""
        for article_num in [8, 9, 10, 11, 12, 13, 14, 15, 30, 40, 49]:
            rule = make_rule(article_number=article_num, check_type="document_required")
            profile = make_profile(ai_act_data={
                "uses_ai": True, "ai_role": "deployer",
                "high_risk_ai_categories": [], "uses_gpai": False
            })
            engine = ApplicabilityEngine(profile, [rule], "EU_AI_ACT")
            result = engine.evaluate()[0]
            assert result.is_applicable is False, \
                f"Art. {article_num} should not apply without high-risk AI"
            assert result.reason == "does_not_operate_high_risk_ai"

    def test_provider_articles_not_applicable_to_pure_deployer(self):
        """Provider obligations not applicable to deployer-only companies."""
        for article_num in [16, 17, 18, 20, 21, 24, 25]:
            rule = make_rule(article_number=article_num, check_type="document_required")
            profile = make_profile(ai_act_data={
                "uses_ai": True, "ai_role": "deployer",
                "high_risk_ai_categories": ["employment"], "uses_gpai": False
            })
            engine = ApplicabilityEngine(profile, [rule], "EU_AI_ACT")
            result = engine.evaluate()[0]
            assert result.is_applicable is False, \
                f"Art. {article_num} should not apply to deployer"
            assert result.reason == "provider_obligations_not_applicable_to_deployers"

    def test_provider_articles_applicable_to_provider(self):
        """Provider obligations applicable to provider companies."""
        rule = make_rule(article_number=16, check_type="document_required")
        engine = ApplicabilityEngine(self._ai_profile(), [rule], "EU_AI_ACT")
        assert engine.evaluate()[0].is_applicable is True

    def test_deployer_articles_not_applicable_to_pure_provider(self):
        """Deployer obligations not applicable to provider-only companies."""
        for article_num in [26, 27]:
            rule = make_rule(article_number=article_num, check_type="policy_required")
            engine = ApplicabilityEngine(self._ai_profile(), [rule], "EU_AI_ACT")
            result = engine.evaluate()[0]
            assert result.is_applicable is False, \
                f"Art. {article_num} should not apply to pure provider"

    def test_deployer_articles_applicable_to_deployer(self):
        """Deployer obligations applicable to deployer companies."""
        for article_num in [26, 27]:
            rule = make_rule(article_number=article_num, check_type="policy_required")
            profile = make_profile(ai_act_data={
                "uses_ai": True, "ai_role": "deployer",
                "high_risk_ai_categories": ["employment"], "uses_gpai": False
            })
            engine = ApplicabilityEngine(profile, [rule], "EU_AI_ACT")
            assert engine.evaluate()[0].is_applicable is True, \
                f"Art. {article_num} should apply to deployer"

    def test_role_both_applies_provider_and_deployer_obligations(self):
        """Role 'both' applies provider AND deployer obligations."""
        profile = make_profile(ai_act_data={
            "uses_ai": True, "ai_role": "both",
            "high_risk_ai_categories": ["employment"], "uses_gpai": False
        })
        provider_rule = make_rule(article_number=16, check_type="document_required")
        deployer_rule = make_rule(article_number=26, check_type="policy_required")
        engine = ApplicabilityEngine(profile, [provider_rule, deployer_rule], "EU_AI_ACT")
        results = engine.evaluate()
        assert results[0].is_applicable is True  # provider rule
        assert results[1].is_applicable is True  # deployer rule

    def test_gpai_articles_not_applicable_without_gpai_model(self):
        """Arts. 51-56 not applicable without GPAI model development."""
        for article_num in range(51, 57):
            rule = make_rule(article_number=article_num, check_type="document_required")
            profile = make_profile(ai_act_data={
                "uses_ai": True, "ai_role": "provider",
                "high_risk_ai_categories": [], "uses_gpai": False
            })
            engine = ApplicabilityEngine(profile, [rule], "EU_AI_ACT")
            result = engine.evaluate()[0]
            assert result.is_applicable is False, \
                f"Art. {article_num} should not apply without GPAI model"
            assert result.reason == "does_not_develop_gpai_models"

    def test_gpai_articles_applicable_with_gpai_model(self):
        """Arts. 51-56 applicable when developing GPAI models."""
        for article_num in range(51, 57):
            rule = make_rule(article_number=article_num, check_type="document_required")
            profile = make_profile(ai_act_data={
                "uses_ai": True, "ai_role": "provider",
                "high_risk_ai_categories": [], "uses_gpai": True
            })
            engine = ApplicabilityEngine(profile, [rule], "EU_AI_ACT")
            assert engine.evaluate()[0].is_applicable is True, \
                f"Art. {article_num} should apply with GPAI model"


# ═══════════════════════════════════════════════════════════════════════════════
# SCORER TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestScorerCheckTypes:
    """Tests for how different check_types are scored."""

    def test_policy_required_returns_unknown(self):
        """policy_required rules return unknown — need policy verification."""
        rule = make_rule(check_type="policy_required", article_number=5)
        scorer = Scorer(make_profile(), [make_applicability_result(rule)], "GDPR")
        assert scorer.evaluate()[0].status == "unknown"

    def test_technical_returns_unknown(self):
        """technical rules return unknown — need technical verification."""
        rule = make_rule(check_type="technical", article_number=32)
        scorer = Scorer(make_profile(), [make_applicability_result(rule)], "GDPR")
        assert scorer.evaluate()[0].status == "unknown"

    def test_document_required_returns_unknown(self):
        """document_required rules return unknown."""
        rule = make_rule(check_type="document_required", article_number=13)
        scorer = Scorer(make_profile(), [make_applicability_result(rule)], "GDPR")
        assert scorer.evaluate()[0].status == "unknown"

    def test_not_applicable_rules_excluded_from_scoring(self):
        """Rules marked not applicable are completely excluded."""
        rule = make_rule(check_type="profile_field", article_number=33)
        ar = make_applicability_result(rule, is_applicable=False, reason="informational_only")
        scorer = Scorer(make_profile(), [ar], "GDPR")
        assert scorer.evaluate() == []

    def test_evidence_recorded_for_unknown_rules(self):
        """Unknown rules have evidence explaining why they can't be evaluated."""
        rule = make_rule(check_type="policy_required")
        scorer = Scorer(make_profile(), [make_applicability_result(rule)], "GDPR")
        result = scorer.evaluate()[0]
        assert "reason" in result.evidence
        assert "policy_required" in result.evidence["reason"]


class TestScorerGDPRRules:
    """Tests for GDPR-specific scoring logic."""

    def _score_article(self, article_num, profile=None, check_type="profile_field"):
        rule = make_rule(article_number=article_num, check_type=check_type)
        ar = make_applicability_result(rule)
        scorer = Scorer(profile or make_profile(), [ar], "GDPR")
        results = scorer.evaluate()
        return results[0] if results else None

    # Art. 6 — Lawful basis
    def test_art6_met_with_lawful_bases(self):
        assert self._score_article(6).status == "met"

    def test_art6_not_met_with_empty_lawful_bases(self):
        profile = make_profile(gdpr_data={**make_profile()["gdpr_data"], "lawful_bases": []})
        assert self._score_article(6, profile).status == "not_met"

    # Art. 8 — Children
    def test_art8_met_when_no_children_data(self):
        """Art. 8 is met when not processing children's data."""
        assert self._score_article(8).status == "met"

    def test_art8_unknown_when_processes_children(self):
        """Art. 8 is unknown when processing children's data (needs verification)."""
        gdpr = {**make_profile()["gdpr_data"], "processes_children_data": True}
        profile = make_profile(gdpr_data=gdpr)
        assert self._score_article(8, profile).status == "unknown"

    # Art. 33/34 — Breach notification
    def test_art33_met_with_breach_procedure(self):
        assert self._score_article(33).status == "met"

    def test_art33_not_met_without_breach_procedure(self):
        gdpr = {**make_profile()["gdpr_data"], "has_breach_procedure": False}
        assert self._score_article(33, make_profile(gdpr_data=gdpr)).status == "not_met"

    def test_art33_unknown_when_breach_procedure_none(self):
        gdpr = {**make_profile()["gdpr_data"], "has_breach_procedure": None}
        assert self._score_article(33, make_profile(gdpr_data=gdpr)).status == "unknown"

    def test_art34_met_with_breach_procedure(self):
        assert self._score_article(34).status == "met"

    def test_art34_not_met_without_breach_procedure(self):
        gdpr = {**make_profile()["gdpr_data"], "has_breach_procedure": False}
        assert self._score_article(34, make_profile(gdpr_data=gdpr)).status == "not_met"

    # Art. 35/36 — DPIA
    def test_art35_met_with_dpia(self):
        assert self._score_article(35).status == "met"

    def test_art35_not_met_without_dpia(self):
        gdpr = {**make_profile()["gdpr_data"], "has_dpia": False}
        assert self._score_article(35, make_profile(gdpr_data=gdpr)).status == "not_met"

    def test_art35_unknown_when_dpia_none(self):
        gdpr = {**make_profile()["gdpr_data"], "has_dpia": None}
        assert self._score_article(35, make_profile(gdpr_data=gdpr)).status == "unknown"

    def test_art36_met_with_dpia(self):
        assert self._score_article(36).status == "met"

    def test_art36_not_met_without_dpia(self):
        gdpr = {**make_profile()["gdpr_data"], "has_dpia": False}
        assert self._score_article(36, make_profile(gdpr_data=gdpr)).status == "not_met"

    # Art. 37/38/39 — DPO
    def test_art37_met_with_dpo_name_and_email(self):
        profile = make_profile(
            has_compliance_officer=True,
            dpo_name="Jane Smith",
            dpo_email="dpo@example.com"
        )
        assert self._score_article(37, profile).status == "met"

    def test_art37_partial_with_dpo_but_missing_email(self):
        profile = make_profile(
            has_compliance_officer=True,
            dpo_name="Jane Smith",
            dpo_email=None
        )
        assert self._score_article(37, profile).status == "partial"

    def test_art37_partial_with_dpo_but_missing_name(self):
        profile = make_profile(
            has_compliance_officer=True,
            dpo_name=None,
            dpo_email="dpo@example.com"
        )
        assert self._score_article(37, profile).status == "partial"

    def test_art37_partial_with_dpo_but_no_details(self):
        profile = make_profile(
            has_compliance_officer=True,
            dpo_name=None,
            dpo_email=None
        )
        assert self._score_article(37, profile).status == "partial"

    def test_art37_unknown_when_no_dpo(self):
        profile = make_profile(has_compliance_officer=False)
        assert self._score_article(37, profile).status == "unknown"

    def test_art37_unknown_when_dpo_none(self):
        profile = make_profile(has_compliance_officer=None)
        assert self._score_article(37, profile).status == "unknown"

    def test_arts38_39_same_logic_as_37(self):
        for article_num in [38, 39]:
            profile_met = make_profile(
                has_compliance_officer=True,
                dpo_name="Jane", dpo_email="dpo@x.com"
            )
            assert self._score_article(article_num, profile_met).status == "met"

    # Arts. 44-49 — International transfers
    def test_transfer_articles_met_with_mechanisms(self):
        gdpr = {**make_profile()["gdpr_data"],
                "transfers_outside_eea": True, "transfer_mechanisms": ["SCCs"]}
        profile = make_profile(gdpr_data=gdpr)
        for article_num in [44, 45, 46, 47, 48, 49]:
            assert self._score_article(article_num, profile).status == "met", \
                f"Art. {article_num} should be met with transfer mechanisms"

    def test_transfer_articles_not_met_without_mechanisms(self):
        gdpr = {**make_profile()["gdpr_data"],
                "transfers_outside_eea": True, "transfer_mechanisms": []}
        profile = make_profile(gdpr_data=gdpr)
        for article_num in [44, 45, 46, 47, 48, 49]:
            assert self._score_article(article_num, profile).status == "not_met", \
                f"Art. {article_num} should be not_met without transfer mechanisms"

    def test_transfer_articles_met_when_no_transfers(self):
        """When no EEA transfers, transfer rules are met (not applicable scenario)."""
        gdpr = {**make_profile()["gdpr_data"], "transfers_outside_eea": False}
        profile = make_profile(gdpr_data=gdpr)
        for article_num in [44, 45, 46]:
            assert self._score_article(article_num, profile).status == "met"

    # Art. 3 — Territorial scope
    def test_art3_met_with_jurisdiction(self):
        assert self._score_article(3).status == "met"

    # Art. 7 — Consent conditions
    def test_art7_unknown(self):
        assert self._score_article(7).status == "unknown"

    # Art. 9 — Special categories
    def test_art9_met_without_special_categories(self):
        assert self._score_article(9).status == "met"

    def test_art9_unknown_with_special_categories(self):
        profile = make_profile(data_categories_processed=["email", "health"])
        assert self._score_article(9, profile).status == "unknown"

    # Art. 10 — Criminal conviction data
    def test_art10_met_without_criminal_data(self):
        assert self._score_article(10).status == "met"

    def test_art10_unknown_with_criminal_data(self):
        profile = make_profile(data_categories_processed=["email", "criminal_convictions"])
        assert self._score_article(10, profile).status == "unknown"

    # Art. 19 — Notification to third parties
    def test_art19_met_without_processors(self):
        gdpr = {**make_profile()["gdpr_data"], "uses_data_processors": False}
        assert self._score_article(19, make_profile(gdpr_data=gdpr)).status == "met"

    def test_art19_unknown_with_processors(self):
        assert self._score_article(19).status == "unknown"

    # Art. 20 — Data portability
    def test_art20_unknown(self):
        assert self._score_article(20).status == "unknown"

    # Art. 27 — EU representative
    def test_art27_unknown(self):
        assert self._score_article(27).status == "unknown"

    # Cross-regulation collision guards — these article numbers also exist
    # in NIS2/AI Act; confirm GDPR's branch is reached only when the rule
    # actually belongs to GDPR (regulation_name dispatch, not article number).
    def test_art3_not_affected_by_nis2_data_present(self):
        """GDPR Art. 3 must not be influenced by nis2_data sitting in the same profile."""
        profile = make_profile(nis2_data={"sectors": [], "entity_type": ""})
        assert self._score_article(3, profile).status == "met"

    def test_art6_not_affected_by_ai_act_data_present(self):
        """GDPR Art. 6 must not be influenced by ai_act_data sitting in the same profile."""
        profile = make_profile(ai_act_data={"uses_ai": True, "high_risk_ai_categories": ["employment"]})
        assert self._score_article(6, profile).status == "met"


class TestScorerAIActRules:
    """Tests for EU AI Act-specific scoring logic."""

    def _ai_act_scorer(self, article_num, ai_act_data=None, profile_kwargs=None):
        rule = make_rule(article_number=article_num, check_type="profile_field")
        profile = make_profile(
            ai_act_data=ai_act_data if ai_act_data is not None else {
                "uses_ai": True, "ai_role": "provider", "high_risk_ai_categories": ["employment"],
            },
            **(profile_kwargs or {}),
        )
        scorer = Scorer(profile, [make_applicability_result(rule)], "EU_AI_ACT")
        results = scorer.evaluate()
        return results[0] if results else None

    # Art. 2 — Scope
    def test_art2_met_with_ai_and_role(self):
        assert self._ai_act_scorer(2).status == "met"

    def test_art2_partial_without_role(self):
        result = self._ai_act_scorer(2, ai_act_data={"uses_ai": True, "ai_role": ""})
        assert result.status == "partial"

    def test_art2_not_influenced_by_nis2_data_present(self):
        """AI Act Art. 2 collides with NIS2's `n in {2,3}` branch — must use ai_act_data, not nis2_data."""
        profile = make_profile(
            ai_act_data={"uses_ai": True, "ai_role": "provider"},
            nis2_data={"sectors": [], "entity_type": ""},
        )
        rule = make_rule(article_number=2, check_type="profile_field")
        scorer = Scorer(profile, [make_applicability_result(rule)], "EU_AI_ACT")
        assert scorer.evaluate()[0].status == "met"

    # Art. 5 — Prohibited practices
    def test_art5_unknown(self):
        assert self._ai_act_scorer(5).status == "unknown"

    # Art. 6 — High-risk classification
    def test_art6_met_with_high_risk_categories(self):
        assert self._ai_act_scorer(6).status == "met"

    def test_art6_not_influenced_by_gdpr_data_present(self):
        """AI Act Art. 6 collides with GDPR's lawful-basis branch — must use high_risk_ai_categories, not lawful_bases."""
        gdpr = {**make_profile()["gdpr_data"], "lawful_bases": []}
        profile = make_profile(
            gdpr_data=gdpr,
            ai_act_data={"uses_ai": True, "high_risk_ai_categories": ["employment"]},
        )
        rule = make_rule(article_number=6, check_type="profile_field")
        scorer = Scorer(profile, [make_applicability_result(rule)], "EU_AI_ACT")
        assert scorer.evaluate()[0].status == "met"

    # Art. 22 — Authorised representative
    def test_art22_unknown_for_non_eu_provider(self):
        result = self._ai_act_scorer(22, ai_act_data={"uses_ai": True, "ai_role": "provider"})
        assert result.status == "unknown"

    def test_art22_met_when_not_a_provider(self):
        result = self._ai_act_scorer(22, ai_act_data={"uses_ai": True, "ai_role": "deployer"})
        assert result.status == "met"

    def test_art22_not_influenced_by_gdpr_data_present(self):
        """AI Act Art. 22 collides with GDPR's automated-decision branch — must use ai_role, not uses_ai alone."""
        profile = make_profile(ai_act_data={"uses_ai": True, "ai_role": "deployer"})
        rule = make_rule(article_number=22, check_type="profile_field")
        scorer = Scorer(profile, [make_applicability_result(rule)], "EU_AI_ACT")
        assert scorer.evaluate()[0].status == "met"

    # Art. 26 — Deployer obligations
    def test_art26_met_for_provider_only(self):
        result = self._ai_act_scorer(26, ai_act_data={"uses_ai": True, "ai_role": "provider"})
        assert result.status == "met"

    def test_art26_unknown_for_deployer_with_high_risk(self):
        result = self._ai_act_scorer(26, ai_act_data={
            "uses_ai": True, "ai_role": "deployer", "high_risk_ai_categories": ["employment"],
        })
        assert result.status == "unknown"

    # Art. 51 — GPAI systemic risk
    def test_art51_met_without_gpai(self):
        result = self._ai_act_scorer(51, ai_act_data={"uses_ai": True, "uses_gpai": False})
        assert result.status == "met"

    def test_art51_unknown_with_gpai(self):
        result = self._ai_act_scorer(51, ai_act_data={"uses_ai": True, "uses_gpai": True})
        assert result.status == "unknown"


class TestScorerNIS2Rules:
    """Tests for NIS2-specific scoring logic."""

    def _nis2_scorer(self, article_num, nis2_data=None):
        rule = make_rule(article_number=article_num, check_type="profile_field")
        profile = make_profile(nis2_data=nis2_data or {
            "sectors": ["energy"],
            "entity_type": "essential",
            "has_incident_response_plan": True,
        })
        scorer = Scorer(profile, [make_applicability_result(rule)], "NIS2")
        results = scorer.evaluate()
        return results[0] if results else None

    def test_nis2_art2_met_with_sectors_and_entity_type(self):
        assert self._nis2_scorer(2).status == "met"

    def test_nis2_art2_partial_without_entity_type(self):
        result = self._nis2_scorer(2, nis2_data={"sectors": ["energy"], "entity_type": ""})
        assert result.status == "partial"

    def test_nis2_art18_met_with_incident_plan(self):
        assert self._nis2_scorer(18).status == "met"

    def test_nis2_art18_not_met_without_incident_plan(self):
        result = self._nis2_scorer(18, nis2_data={
            "sectors": ["energy"], "entity_type": "essential", "has_incident_response_plan": False
        })
        assert result.status == "not_met"

    def test_nis2_art23_unknown_when_incident_plan_none(self):
        result = self._nis2_scorer(23, nis2_data={
            "sectors": ["energy"], "entity_type": "essential", "has_incident_response_plan": None
        })
        assert result.status == "unknown"

    def test_nis2_art3_met_with_sectors_and_entity_type(self):
        assert self._nis2_scorer(3).status == "met"

    def test_nis2_art27_unknown(self):
        assert self._nis2_scorer(27).status == "unknown"

    def test_nis2_art3_not_influenced_by_gdpr_jurisdiction(self):
        """NIS2 Art. 3 collides with GDPR's territorial-scope branch — must use sectors/entity_type, not jurisdiction."""
        rule = make_rule(article_number=3, check_type="profile_field")
        profile = make_profile(
            primary_jurisdiction="",
            nis2_data={"sectors": ["energy"], "entity_type": "essential"},
        )
        scorer = Scorer(profile, [make_applicability_result(rule)], "NIS2")
        assert scorer.evaluate()[0].status == "met"


class TestScorerOverallScore:
    """Tests for the overall score calculation."""

    def test_empty_results_gives_score_zero(self):
        scorer = Scorer(make_profile(), [], "GDPR")
        summary = scorer.calculate_overall_score([])
        assert summary["score"] == 0
        assert summary["total_rules"] == 0

    def test_all_met_gives_score_100(self):
        results = [make_scoring_result(make_rule(severity=Severity.HIGH), "met")]
        scorer = Scorer(make_profile(), [], "GDPR")
        summary = scorer.calculate_overall_score(results)
        assert summary["score"] == 100
        assert summary["risk_level"] == "low"

    def test_all_not_met_gives_score_zero(self):
        results = [make_scoring_result(make_rule(severity=Severity.HIGH), "not_met")]
        scorer = Scorer(make_profile(), [], "GDPR")
        summary = scorer.calculate_overall_score(results)
        assert summary["score"] == 0
        assert summary["risk_level"] == "critical"

    def test_all_unknown_gives_score_zero(self):
        """All unknown rules → score is 0 (no weight to calculate from)."""
        results = [make_scoring_result(make_rule(severity=Severity.HIGH), "unknown")]
        scorer = Scorer(make_profile(), [], "GDPR")
        summary = scorer.calculate_overall_score(results)
        assert summary["score"] == 0
        assert summary["unknown_rules"] == 1

    def test_partial_rule_gives_50_percent(self):
        """Single partial rule → score is 50."""
        results = [make_scoring_result(make_rule(severity=Severity.MEDIUM), "partial")]
        scorer = Scorer(make_profile(), [], "GDPR")
        summary = scorer.calculate_overall_score(results)
        assert summary["score"] == 50

    def test_unknown_rules_excluded_from_score_calculation(self):
        """Unknown rules don't affect the score denominator."""
        met_rule = make_scoring_result(make_rule(severity=Severity.HIGH), "met")
        unknown_rule = make_scoring_result(make_rule(severity=Severity.CRITICAL), "unknown")
        scorer = Scorer(make_profile(), [], "GDPR")
        summary = scorer.calculate_overall_score([met_rule, unknown_rule])
        # Score is based only on met_rule (weight=3), unknown excluded
        assert summary["score"] == 100
        assert summary["unknown_rules"] == 1

    def test_severity_weighting_critical_counts_more(self):
        """Critical rules (weight=4) have more impact than low rules (weight=1)."""
        critical_met = make_scoring_result(make_rule(severity=Severity.CRITICAL), "met")
        low_not_met = make_scoring_result(make_rule(severity=Severity.LOW), "not_met")
        scorer = Scorer(make_profile(), [], "GDPR")
        summary = scorer.calculate_overall_score([critical_met, low_not_met])
        # earned=4, total=5, score=80
        assert summary["score"] == 80
        assert summary["risk_level"] == "low"

    def test_risk_level_critical_below_40(self):
        """Risk level is critical when score < 40."""
        results = [make_scoring_result(make_rule(severity=Severity.CRITICAL), "not_met")]
        scorer = Scorer(make_profile(), [], "GDPR")
        summary = scorer.calculate_overall_score(results)
        assert summary["risk_level"] == "critical"
        assert summary["score"] == 0

    def test_risk_level_high_between_40_and_60(self):
        """Risk level is high when 40 <= score < 60."""
        # 2 met, 3 not_met of same severity → 2/5 = 40%
        results = [
            make_scoring_result(make_rule(severity=Severity.MEDIUM), "met"),
            make_scoring_result(make_rule(severity=Severity.MEDIUM), "met"),
            make_scoring_result(make_rule(severity=Severity.MEDIUM), "not_met"),
            make_scoring_result(make_rule(severity=Severity.MEDIUM), "not_met"),
            make_scoring_result(make_rule(severity=Severity.MEDIUM), "not_met"),
        ]
        scorer = Scorer(make_profile(), [], "GDPR")
        summary = scorer.calculate_overall_score(results)
        assert summary["score"] == 40
        assert summary["risk_level"] == "high"

    def test_risk_level_medium_between_60_and_80(self):
        """Risk level is medium when 60 <= score < 80."""
        results = [
            make_scoring_result(make_rule(severity=Severity.MEDIUM), "met"),
            make_scoring_result(make_rule(severity=Severity.MEDIUM), "met"),
            make_scoring_result(make_rule(severity=Severity.MEDIUM), "met"),
            make_scoring_result(make_rule(severity=Severity.MEDIUM), "not_met"),
            make_scoring_result(make_rule(severity=Severity.MEDIUM), "not_met"),
        ]
        scorer = Scorer(make_profile(), [], "GDPR")
        summary = scorer.calculate_overall_score(results)
        assert summary["score"] == 60
        assert summary["risk_level"] == "medium"

    def test_risk_level_low_at_80_or_above(self):
        """Risk level is low when score >= 80."""
        results = [
            make_scoring_result(make_rule(severity=Severity.MEDIUM), "met"),
            make_scoring_result(make_rule(severity=Severity.MEDIUM), "met"),
            make_scoring_result(make_rule(severity=Severity.MEDIUM), "met"),
            make_scoring_result(make_rule(severity=Severity.MEDIUM), "met"),
            make_scoring_result(make_rule(severity=Severity.MEDIUM), "not_met"),
        ]
        scorer = Scorer(make_profile(), [], "GDPR")
        summary = scorer.calculate_overall_score(results)
        assert summary["score"] == 80
        assert summary["risk_level"] == "low"

    def test_score_counts_accurate(self):
        """Score summary counts match actual results."""
        results = [
            make_scoring_result(make_rule(), "met"),
            make_scoring_result(make_rule(), "met"),
            make_scoring_result(make_rule(), "partial"),
            make_scoring_result(make_rule(), "not_met"),
            make_scoring_result(make_rule(), "unknown"),
        ]
        scorer = Scorer(make_profile(), [], "GDPR")
        summary = scorer.calculate_overall_score(results)
        assert summary["met_rules"] == 2
        assert summary["partial_rules"] == 1
        assert summary["not_met_rules"] == 1
        assert summary["unknown_rules"] == 1
        assert summary["total_rules"] == 5

    def test_remediation_priority_none_for_met_rules(self):
        """Met rules have no remediation priority."""
        rule = make_rule(check_type="profile_field", article_number=33)
        scorer = Scorer(make_profile(), [make_applicability_result(rule)], "GDPR")
        results = scorer.evaluate()
        assert results[0].remediation_priority is None

    def test_remediation_priority_matches_severity_for_not_met(self):
        """Not met rules get remediation priority matching their severity."""
        for severity, expected_priority in [
            (Severity.CRITICAL, "critical"),
            (Severity.HIGH, "high"),
            (Severity.MEDIUM, "medium"),
            (Severity.LOW, "low"),
        ]:
            rule = make_rule(check_type="policy_required", severity=severity)
            scorer = Scorer(make_profile(), [make_applicability_result(rule)], "GDPR")
            result = scorer.evaluate()[0]
            assert result.remediation_priority == expected_priority


# ═══════════════════════════════════════════════════════════════════════════════
# REMEDIATION GENERATOR TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestRemediationGenerator:
    """Tests for the remediation generator."""

    def test_empty_results_returns_empty_list(self):
        """Empty scoring results → no remediation items."""
        gen = RemediationGenerator([])
        assert gen.generate() == []

    def test_all_met_returns_empty_list(self):
        """All met rules → nothing to remediate."""
        results = [make_scoring_result(make_rule(), "met") for _ in range(5)]
        gen = RemediationGenerator(results)
        assert gen.generate() == []

    def test_not_met_rules_included(self):
        """Not met rules are in the remediation list."""
        result = make_scoring_result(make_rule(), "not_met")
        gen = RemediationGenerator([result])
        items = gen.generate()
        assert len(items) == 1
        assert items[0].status == "not_met"

    def test_partial_rules_included(self):
        """Partial rules are in the remediation list."""
        result = make_scoring_result(make_rule(), "partial")
        gen = RemediationGenerator([result])
        items = gen.generate()
        assert len(items) == 1
        assert items[0].status == "partial"

    def test_unknown_rules_included(self):
        """Unknown rules are in the remediation list."""
        result = make_scoring_result(make_rule(), "unknown")
        gen = RemediationGenerator([result])
        items = gen.generate()
        assert len(items) == 1
        assert items[0].status == "unknown"

    def test_met_rules_excluded(self):
        """Met rules excluded — only non-met rules appear."""
        results = [
            make_scoring_result(make_rule(), "met"),
            make_scoring_result(make_rule(), "not_met"),
            make_scoring_result(make_rule(), "met"),
        ]
        gen = RemediationGenerator(results)
        items = gen.generate()
        assert len(items) == 1
        assert items[0].status == "not_met"

    def test_evidence_needed_for_policy_required_unknown(self):
        """Unknown policy_required rules have evidence_needed guidance."""
        rule = make_rule(check_type="policy_required")
        result = make_scoring_result(rule, "unknown")
        gen = RemediationGenerator([result])
        item = gen.generate()[0]
        assert item.evidence_needed is not None
        assert "policy" in item.evidence_needed.lower()

    def test_evidence_needed_for_document_required_unknown(self):
        """Unknown document_required rules have evidence_needed guidance."""
        rule = make_rule(check_type="document_required")
        result = make_scoring_result(rule, "unknown")
        gen = RemediationGenerator([result])
        item = gen.generate()[0]
        assert item.evidence_needed is not None
        assert "document" in item.evidence_needed.lower()

    def test_evidence_needed_for_technical_unknown(self):
        """Unknown technical rules have evidence_needed guidance."""
        rule = make_rule(check_type="technical")
        result = make_scoring_result(rule, "unknown")
        gen = RemediationGenerator([result])
        item = gen.generate()[0]
        assert item.evidence_needed is not None
        assert "technical" in item.evidence_needed.lower()

    def test_no_evidence_needed_for_not_met_rules(self):
        """Not met rules don't need evidence — we know they failed."""
        result = make_scoring_result(make_rule(), "not_met")
        gen = RemediationGenerator([result])
        item = gen.generate()[0]
        assert item.evidence_needed is None

    def test_no_evidence_needed_for_partial_rules(self):
        """Partial rules don't need evidence — we know they partially passed."""
        result = make_scoring_result(make_rule(), "partial")
        gen = RemediationGenerator([result])
        item = gen.generate()[0]
        assert item.evidence_needed is None

    def test_fine_exposure_tier_2(self):
        """Tier 2 rules show correct maximum fine."""
        rule = make_rule(fine_tier="tier_2")
        result = make_scoring_result(rule, "not_met")
        gen = RemediationGenerator([result])
        item = gen.generate()[0]
        assert item.fine_exposure == "Up to €20M or 4% of global annual turnover"

    def test_fine_exposure_tier_1(self):
        """Tier 1 rules show correct maximum fine."""
        rule = make_rule(fine_tier="tier_1")
        result = make_scoring_result(rule, "not_met")
        gen = RemediationGenerator([result])
        item = gen.generate()[0]
        assert item.fine_exposure == "Up to €10M or 2% of global annual turnover"

    def test_fine_exposure_none_when_no_tier(self):
        """Rules with no fine tier have None exposure."""
        rule = make_rule(fine_tier=None)
        result = make_scoring_result(rule, "not_met")
        gen = RemediationGenerator([result])
        item = gen.generate()[0]
        assert item.fine_exposure is None

    def test_remediation_steps_from_rule(self):
        """Remediation steps pulled from rule's seeded data."""
        rule = make_rule(remediation_steps={"steps": ["Step A", "Step B"]})
        result = make_scoring_result(rule, "not_met")
        gen = RemediationGenerator([result])
        item = gen.generate()[0]
        assert item.remediation_steps == ["Step A", "Step B"]

    def test_remediation_steps_fallback_to_hint(self):
        """When no steps seeded, uses remediation_hint as fallback."""
        rule = make_rule(
            remediation_steps={"steps": []},
            remediation_hint="Do this specific thing."
        )
        result = make_scoring_result(rule, "not_met")
        gen = RemediationGenerator([result])
        item = gen.generate()[0]
        assert item.remediation_steps == ["Do this specific thing."]

    def test_remediation_steps_empty_when_no_steps_and_no_hint(self):
        """Empty steps and no hint → empty steps list."""
        rule = make_rule(
            remediation_steps={"steps": []},
            remediation_hint=None
        )
        result = make_scoring_result(rule, "not_met")
        gen = RemediationGenerator([result])
        item = gen.generate()[0]
        assert item.remediation_steps == []

    def test_remediation_resources_from_rule(self):
        """Resources pulled from rule's seeded links."""
        rule = make_rule(remediation_resources={"links": [{"label": "GDPR Guide", "url": "https://example.com"}]})
        result = make_scoring_result(rule, "not_met")
        gen = RemediationGenerator([result])
        item = gen.generate()[0]
        assert len(item.remediation_resources) == 1
        assert item.remediation_resources[0]["label"] == "GDPR Guide"

    def test_remediation_resources_empty_when_no_links(self):
        """Empty links → empty resources list."""
        rule = make_rule(remediation_resources={"links": []})
        result = make_scoring_result(rule, "not_met")
        gen = RemediationGenerator([result])
        item = gen.generate()[0]
        assert item.remediation_resources == []

    def test_priority_ordering_critical_not_met_first(self):
        """Critical not_met rules come before everything else."""
        items_unordered = [
            make_scoring_result(make_rule(severity=Severity.HIGH, check_type="policy_required"), "unknown", "high"),
            make_scoring_result(make_rule(severity=Severity.LOW), "not_met", "low"),
            make_scoring_result(make_rule(severity=Severity.CRITICAL), "not_met", "critical"),
            make_scoring_result(make_rule(severity=Severity.MEDIUM), "partial", "medium"),
        ]
        gen = RemediationGenerator(items_unordered)
        items = gen.generate()
        assert items[0].rule.severity == Severity.CRITICAL
        assert items[0].status == "not_met"

    def test_priority_ordering_full_sequence(self):
        """Verify full priority ordering matches spec."""
        results = [
            make_scoring_result(make_rule(severity=Severity.LOW), "partial", "low"),
            make_scoring_result(make_rule(severity=Severity.LOW), "unknown", "low"),
            make_scoring_result(make_rule(severity=Severity.LOW), "not_met", "low"),
            make_scoring_result(make_rule(severity=Severity.HIGH), "partial", "high"),
            make_scoring_result(make_rule(severity=Severity.HIGH), "unknown", "high"),
            make_scoring_result(make_rule(severity=Severity.HIGH), "not_met", "high"),
            make_scoring_result(make_rule(severity=Severity.CRITICAL), "partial", "critical"),
            make_scoring_result(make_rule(severity=Severity.CRITICAL), "unknown", "critical"),
            make_scoring_result(make_rule(severity=Severity.CRITICAL), "not_met", "critical"),
        ]
        gen = RemediationGenerator(results)
        items = gen.generate()
        # First item must be critical not_met
        assert items[0].status == "not_met"
        assert items[0].rule.severity == Severity.CRITICAL
        # Second item must be high not_met
        assert items[1].status == "not_met"
        assert items[1].rule.severity == Severity.HIGH

    def test_summary_empty_when_no_items(self):
        """Summary with no items returns all zeros."""
        gen = RemediationGenerator([])
        summary = gen.summary([])
        assert summary["total_action_items"] == 0
        assert summary["immediate_action_required"] is False
        assert all(v == 0 for v in summary["by_priority"].values())

    def test_summary_immediate_action_when_critical(self):
        """immediate_action_required is True when critical items exist."""
        rule = make_rule(severity=Severity.CRITICAL)
        result = make_scoring_result(rule, "not_met", "critical")
        gen = RemediationGenerator([result])
        items = gen.generate()
        summary = gen.summary(items)
        assert summary["immediate_action_required"] is True
        assert summary["by_priority"]["critical"] == 1

    def test_summary_no_immediate_action_when_only_medium_low(self):
        """immediate_action_required is False when only medium/low items."""
        results = [
            make_scoring_result(make_rule(severity=Severity.MEDIUM), "not_met", "medium"),
            make_scoring_result(make_rule(severity=Severity.LOW), "not_met", "low"),
        ]
        gen = RemediationGenerator(results)
        items = gen.generate()
        summary = gen.summary(items)
        assert summary["immediate_action_required"] is False

    def test_summary_by_status_counts(self):
        """Summary by_status counts match actual results."""
        results = [
            make_scoring_result(make_rule(), "not_met"),
            make_scoring_result(make_rule(), "not_met"),
            make_scoring_result(make_rule(), "partial"),
            make_scoring_result(make_rule(), "unknown"),
        ]
        gen = RemediationGenerator(results)
        items = gen.generate()
        summary = gen.summary(items)
        assert summary["by_status"]["not_met"] == 2
        assert summary["by_status"]["partial"] == 1
        assert summary["by_status"]["unknown"] == 1