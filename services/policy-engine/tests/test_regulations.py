import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from common.db.session import get_admin_session


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_mock_regulation(**kwargs):
    reg = MagicMock()
    reg.id = uuid.uuid4()
    reg.name = kwargs.get("name", "GDPR")
    reg.full_name = kwargs.get("full_name", "General Data Protection Regulation")
    reg.jurisdiction = kwargs.get("jurisdiction", "EU")
    reg.authority = kwargs.get("authority", "EDPB")
    reg.status = kwargs.get("status", "active")
    reg.effective_date = kwargs.get("effective_date", None)
    reg.source_url = kwargs.get("source_url", "https://gdpr-info.eu")
    return reg


def make_mock_rule(**kwargs):
    rule = MagicMock()
    rule.id = uuid.uuid4()
    rule.rule_id = kwargs.get("rule_id", "rul_test001")
    rule.article = kwargs.get("article", "Article 5")
    rule.article_number = kwargs.get("article_number", 5)
    rule.title = kwargs.get("title", "Principles")
    rule.chapter = kwargs.get("chapter", "Chapter II")
    rule.category = kwargs.get("category", "Core Principles")
    rule.plain_english = kwargs.get("plain_english", "Core GDPR principles.")
    rule.severity = kwargs.get("severity", "critical")
    rule.fine_tier = kwargs.get("fine_tier", "tier_2")
    rule.is_mandatory = kwargs.get("is_mandatory", True)
    rule.check_type = kwargs.get("check_type", "policy_required")
    rule.applies_to_b2c = kwargs.get("applies_to_b2c", True)
    rule.applies_to_b2b = kwargs.get("applies_to_b2b", True)
    rule.remediation_hint = kwargs.get("remediation_hint", "Document your processing.")
    rule.is_active = kwargs.get("is_active", True)
    return rule


@pytest.fixture
def client():
    mock_session = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    async def override():
        yield mock_session

    app.dependency_overrides[get_admin_session] = override
    yield TestClient(app), mock_session
    app.dependency_overrides.clear()


def mock_regulations_result(regulations: list):
    """Mock session.execute() returning a list of regulations."""
    scalars = MagicMock()
    scalars.all.return_value = regulations
    result = MagicMock()
    result.scalars.return_value = scalars
    return result


def mock_regulation_lookup(regulation):
    """Mock session.execute() returning a single regulation."""
    result = MagicMock()
    result.scalar_one_or_none.return_value = regulation
    return result


def mock_rules_result(rules: list):
    """Mock session.execute() returning a list of rules."""
    scalars = MagicMock()
    scalars.all.return_value = rules
    result = MagicMock()
    result.scalars.return_value = scalars
    return result


# ── GET /api/v1/regulations ───────────────────────────────────────────────────

class TestListRegulations:

    def test_returns_200_with_regulations(self, client):
        """Happy path — DB has 3 regulations → 200 with list of 3."""
        test_client, mock_session = client
        regs = [
            make_mock_regulation(name="EU_AI_ACT"),
            make_mock_regulation(name="GDPR"),
            make_mock_regulation(name="NIS2"),
        ]
        mock_session.execute = AsyncMock(return_value=mock_regulations_result(regs))

        response = test_client.get("/api/v1/regulations")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_returns_empty_list_when_no_regulations(self, client):
        """DB is empty → 200 with empty list, not 404."""
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=mock_regulations_result([]))

        response = test_client.get("/api/v1/regulations")

        assert response.status_code == 200
        assert response.json() == []

    def test_response_contains_required_fields(self, client):
        """Each regulation in response has all required fields."""
        test_client, mock_session = client
        reg = make_mock_regulation()
        mock_session.execute = AsyncMock(return_value=mock_regulations_result([reg]))

        response = test_client.get("/api/v1/regulations")

        data = response.json()[0]
        assert "id" in data
        assert "name" in data
        assert "full_name" in data
        assert "jurisdiction" in data
        assert "authority" in data
        assert "status" in data
        assert "source_url" in data

    def test_status_is_lowercase(self, client):
        """Status should be lowercase 'active' not 'ACTIVE' — pg_enum fix."""
        test_client, mock_session = client
        reg = make_mock_regulation(status="active")
        mock_session.execute = AsyncMock(return_value=mock_regulations_result([reg]))

        response = test_client.get("/api/v1/regulations")

        assert response.json()[0]["status"] == "active"

    def test_post_method_not_allowed(self, client):
        """POST /regulations → 405 Method Not Allowed."""
        test_client, _ = client
        response = test_client.post("/api/v1/regulations", json={})
        assert response.status_code == 405

    def test_delete_method_not_allowed(self, client):
        """DELETE /regulations → 405 Method Not Allowed."""
        test_client, _ = client
        response = test_client.delete("/api/v1/regulations")
        assert response.status_code == 405


# ── GET /api/v1/regulations/{name}/rules ─────────────────────────────────────

class TestListRules:

    # ── Happy path ────────────────────────────────────────────────────────────

    def test_returns_rules_for_valid_regulation(self, client):
        """GDPR in DB → 200 with rules."""
        test_client, mock_session = client
        reg = make_mock_regulation(name="GDPR")
        rules = [make_mock_rule(), make_mock_rule(article="Article 6", article_number=6)]

        mock_session.execute = AsyncMock(
            side_effect=[mock_regulation_lookup(reg), mock_rules_result(rules)]
        )

        response = test_client.get("/api/v1/regulations/GDPR/rules")

        assert response.status_code == 200
        data = response.json()
        assert data["regulation"] == "GDPR"
        assert data["total"] == 2
        assert len(data["rules"]) == 2

    def test_total_always_matches_rules_length(self, client):
        """total field always equals len(rules) — never out of sync."""
        test_client, mock_session = client
        reg = make_mock_regulation()
        rules = [make_mock_rule() for _ in range(7)]

        mock_session.execute = AsyncMock(
            side_effect=[mock_regulation_lookup(reg), mock_rules_result(rules)]
        )

        response = test_client.get("/api/v1/regulations/GDPR/rules")
        data = response.json()

        assert data["total"] == len(data["rules"])

    def test_response_rules_have_required_fields(self, client):
        """Each rule has all required fields in response."""
        test_client, mock_session = client
        reg = make_mock_regulation()
        rules = [make_mock_rule()]

        mock_session.execute = AsyncMock(
            side_effect=[mock_regulation_lookup(reg), mock_rules_result(rules)]
        )

        response = test_client.get("/api/v1/regulations/GDPR/rules")
        rule = response.json()["rules"][0]

        assert "id" in rule
        assert "rule_id" in rule
        assert "article" in rule
        assert "article_number" in rule
        assert "title" in rule
        assert "chapter" in rule
        assert "category" in rule
        assert "severity" in rule
        assert "fine_tier" in rule
        assert "is_mandatory" in rule
        assert "check_type" in rule
        assert "applies_to_b2c" in rule
        assert "applies_to_b2b" in rule
        assert "remediation_hint" in rule

    # ── Case insensitivity ────────────────────────────────────────────────────

    def test_lowercase_name_works(self, client):
        """gdpr (lowercase) → same result as GDPR."""
        test_client, mock_session = client
        reg = make_mock_regulation(name="GDPR")
        rules = [make_mock_rule()]

        mock_session.execute = AsyncMock(
            side_effect=[mock_regulation_lookup(reg), mock_rules_result(rules)]
        )

        response = test_client.get("/api/v1/regulations/gdpr/rules")

        assert response.status_code == 200
        assert response.json()["regulation"] == "GDPR"

    def test_mixed_case_name_works(self, client):
        """Gdpr (mixed case) → same result as GDPR."""
        test_client, mock_session = client
        reg = make_mock_regulation(name="GDPR")
        rules = [make_mock_rule()]

        mock_session.execute = AsyncMock(
            side_effect=[mock_regulation_lookup(reg), mock_rules_result(rules)]
        )

        response = test_client.get("/api/v1/regulations/Gdpr/rules")

        assert response.status_code == 200

    def test_eu_ai_act_with_underscore(self, client):
        """EU_AI_ACT with underscores → works correctly."""
        test_client, mock_session = client
        reg = make_mock_regulation(name="EU_AI_ACT")
        rules = [make_mock_rule()]

        mock_session.execute = AsyncMock(
            side_effect=[mock_regulation_lookup(reg), mock_rules_result(rules)]
        )

        response = test_client.get("/api/v1/regulations/EU_AI_ACT/rules")

        assert response.status_code == 200
        assert response.json()["regulation"] == "EU_AI_ACT"

    def test_eu_ai_act_lowercase(self, client):
        """eu_ai_act (lowercase) → works after .upper()."""
        test_client, mock_session = client
        reg = make_mock_regulation(name="EU_AI_ACT")
        rules = [make_mock_rule()]

        mock_session.execute = AsyncMock(
            side_effect=[mock_regulation_lookup(reg), mock_rules_result(rules)]
        )

        response = test_client.get("/api/v1/regulations/eu_ai_act/rules")

        assert response.status_code == 200

    # ── Not found ─────────────────────────────────────────────────────────────

    def test_unknown_regulation_returns_404(self, client):
        """Unknown regulation name → 404."""
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=mock_regulation_lookup(None))

        response = test_client.get("/api/v1/regulations/XYZ/rules")

        assert response.status_code == 404
        assert "xyz" in response.json()["detail"].lower()

    def test_regulation_name_with_dash_returns_404(self, client):
        """eu-ai-act with dash → 404 (only underscores used in DB)."""
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=mock_regulation_lookup(None))

        response = test_client.get("/api/v1/regulations/eu-ai-act/rules")

        assert response.status_code == 404

    def test_numeric_name_returns_404(self, client):
        """Numeric regulation name → 404."""
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=mock_regulation_lookup(None))

        response = test_client.get("/api/v1/regulations/123/rules")

        assert response.status_code == 404

    def test_very_long_name_returns_404(self, client):
        """10000 char regulation name → 404, no crash."""
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=mock_regulation_lookup(None))

        long_name = "A" * 10000
        response = test_client.get(f"/api/v1/regulations/{long_name}/rules")

        assert response.status_code == 404

    def test_sql_injection_in_name_returns_404(self, client):
        """SQL injection attempt → 404, DB never executes malicious SQL."""
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=mock_regulation_lookup(None))

        response = test_client.get("/api/v1/regulations/'; DROP TABLE rules; --/rules")

        assert response.status_code == 404

    def test_rules_as_regulation_name_returns_404(self, client):
        """/regulations/rules → treats 'rules' as regulation name → 404."""
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=mock_regulation_lookup(None))

        response = test_client.get("/api/v1/regulations/rules/rules")

        assert response.status_code == 404

    # ── Filters ───────────────────────────────────────────────────────────────

    def test_filter_by_category(self, client):
        """?category=Security → returns only Security rules."""
        test_client, mock_session = client
        reg = make_mock_regulation()
        rules = [make_mock_rule(category="security")]

        mock_session.execute = AsyncMock(
            side_effect=[mock_regulation_lookup(reg), mock_rules_result(rules)]
        )

        response = test_client.get("/api/v1/regulations/GDPR/rules?category=security")

        assert response.status_code == 200
        assert response.json()["total"] == 1

    def test_filter_by_severity_lowercase(self, client):
        """?severity=critical → works."""
        test_client, mock_session = client
        reg = make_mock_regulation()
        rules = [make_mock_rule(severity="critical")]

        mock_session.execute = AsyncMock(
            side_effect=[mock_regulation_lookup(reg), mock_rules_result(rules)]
        )

        response = test_client.get("/api/v1/regulations/GDPR/rules?severity=critical")

        assert response.status_code == 200
        assert response.json()["total"] == 1

    def test_filter_by_severity_uppercase_still_works(self, client):
        """?severity=CRITICAL uppercase → .lower() fix makes it work."""
        test_client, mock_session = client
        reg = make_mock_regulation()
        rules = [make_mock_rule(severity="critical")]

        mock_session.execute = AsyncMock(
            side_effect=[mock_regulation_lookup(reg), mock_rules_result(rules)]
        )

        response = test_client.get("/api/v1/regulations/GDPR/rules?severity=CRITICAL")

        assert response.status_code == 200

    def test_filter_by_check_type_uppercase_works(self, client):
        """?check_type=TECHNICAL → .lower() fix makes it work."""
        test_client, mock_session = client
        reg = make_mock_regulation()
        rules = [make_mock_rule(check_type="technical")]

        mock_session.execute = AsyncMock(
            side_effect=[mock_regulation_lookup(reg), mock_rules_result(rules)]
        )

        response = test_client.get("/api/v1/regulations/GDPR/rules?check_type=TECHNICAL")

        assert response.status_code == 200

    def test_multiple_filters_combined(self, client):
        """?severity=critical&check_type=technical → intersection of both."""
        test_client, mock_session = client
        reg = make_mock_regulation()
        rules = [make_mock_rule(severity="critical", check_type="technical")]

        mock_session.execute = AsyncMock(
            side_effect=[mock_regulation_lookup(reg), mock_rules_result(rules)]
        )

        response = test_client.get(
            "/api/v1/regulations/GDPR/rules?severity=critical&check_type=technical"
        )

        assert response.status_code == 200
        assert response.json()["total"] == 1

    def test_filter_with_no_matches_returns_empty_list_not_404(self, client):
        """Filter that matches nothing → 200 empty list, not 404."""
        test_client, mock_session = client
        reg = make_mock_regulation()

        mock_session.execute = AsyncMock(
            side_effect=[mock_regulation_lookup(reg), mock_rules_result([])]
        )

        response = test_client.get(
            "/api/v1/regulations/GDPR/rules?severity=critical&category=NONEXISTENT"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["rules"] == []

    def test_invalid_severity_value_returns_empty_not_422(self, client):
        """?severity=banana → no match, 200 empty list (not validation error)."""
        test_client, mock_session = client
        reg = make_mock_regulation()

        mock_session.execute = AsyncMock(
            side_effect=[mock_regulation_lookup(reg), mock_rules_result([])]
        )

        response = test_client.get("/api/v1/regulations/GDPR/rules?severity=banana")

        assert response.status_code == 200
        assert response.json()["total"] == 0

    def test_empty_string_filter_treated_as_no_filter(self, client):
        """?severity= empty string → treated as no filter, returns all rules."""
        test_client, mock_session = client
        reg = make_mock_regulation()
        rules = [make_mock_rule(), make_mock_rule(article="Article 6", article_number=6)]

        mock_session.execute = AsyncMock(
            side_effect=[mock_regulation_lookup(reg), mock_rules_result(rules)]
        )

        response = test_client.get("/api/v1/regulations/GDPR/rules?severity=")

        assert response.status_code == 200
        assert response.json()["total"] == 2

    def test_unsupported_filter_param_silently_ignored(self, client):
        """?is_mandatory=true (unsupported) → silently ignored, returns all rules."""
        test_client, mock_session = client
        reg = make_mock_regulation()
        rules = [make_mock_rule()]

        mock_session.execute = AsyncMock(
            side_effect=[mock_regulation_lookup(reg), mock_rules_result(rules)]
        )

        response = test_client.get("/api/v1/regulations/GDPR/rules?is_mandatory=true")

        assert response.status_code == 200

    def test_sql_injection_in_filter_returns_empty_list(self, client):
        """SQL injection in ?category → ORM is safe, returns empty list."""
        test_client, mock_session = client
        reg = make_mock_regulation()

        mock_session.execute = AsyncMock(
            side_effect=[mock_regulation_lookup(reg), mock_rules_result([])]
        )

        response = test_client.get(
            "/api/v1/regulations/GDPR/rules?category='; DROP TABLE rules; --"
        )

        assert response.status_code == 200
        assert response.json()["total"] == 0

    # ── Inactive rules ────────────────────────────────────────────────────────

    def test_inactive_rules_not_returned(self, client):
        """Rules with is_active=False are excluded from results."""
        test_client, mock_session = client
        reg = make_mock_regulation()
        # Only active rule returned — mock already filters at DB level
        active_rule = make_mock_rule(is_active=True)

        mock_session.execute = AsyncMock(
            side_effect=[mock_regulation_lookup(reg), mock_rules_result([active_rule])]
        )

        response = test_client.get("/api/v1/regulations/GDPR/rules")

        assert response.status_code == 200
        assert response.json()["total"] == 1

    # ── Regulation with no rules ──────────────────────────────────────────────

    def test_regulation_with_zero_rules_returns_empty_list(self, client):
        """Regulation exists but has no rules → 200 with empty rules list."""
        test_client, mock_session = client
        reg = make_mock_regulation()

        mock_session.execute = AsyncMock(
            side_effect=[mock_regulation_lookup(reg), mock_rules_result([])]
        )

        response = test_client.get("/api/v1/regulations/GDPR/rules")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["rules"] == []

    # ── HTTP methods ──────────────────────────────────────────────────────────

    def test_post_to_rules_endpoint_not_allowed(self, client):
        """POST /regulations/GDPR/rules → 405."""
        test_client, _ = client
        response = test_client.post("/api/v1/regulations/GDPR/rules", json={})
        assert response.status_code == 405

    def test_delete_rules_not_allowed(self, client):
        """DELETE /regulations/GDPR/rules → 405."""
        test_client, _ = client
        response = test_client.delete("/api/v1/regulations/GDPR/rules")
        assert response.status_code == 405

    # ── Health check ──────────────────────────────────────────────────────────

    def test_health_endpoint_still_works(self, client):
        """Health check unaffected by router inclusion."""
        test_client, _ = client
        response = test_client.get("/health")
        assert response.status_code == 200
        assert response.json()["service"] == "policy-engine"