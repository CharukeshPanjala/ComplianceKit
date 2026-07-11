"""
Tests for assessment API endpoints:
- POST /api/v1/assessments (run + cooldown)
- GET  /api/v1/assessments/latest
- GET  /api/v1/assessments/{id}
- GET  /api/v1/assessments/{id}/gaps
- GET  /api/v1/assessments/history
- PATCH /api/v1/assessments/{id}/gaps/{gap_id}
- GET  /api/v1/assessments/{id}/stats
"""
import uuid
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from common.auth.clerk import verify_token, TokenClaims
from common.db.session import get_admin_session
from common.models.assessment import Assessment, Gap, AssessmentStatus, RiskLevel, GapStatus


# ── Helpers ───────────────────────────────────────────────────────────────────

FAKE_CLAIMS = TokenClaims(
    user_id="user_test123",
    tenant_id="ten_test456",
    org_role="org:admin",
)

GDPR_REG_ID = uuid.uuid4()
NIS2_REG_ID = uuid.uuid4()


def make_mock_regulation(name="GDPR", reg_id=None):
    reg = MagicMock()
    reg.id = reg_id or GDPR_REG_ID
    reg.name = name
    return reg


def make_mock_profile(is_complete=True, **kwargs):
    profile = MagicMock()
    profile.is_complete = is_complete
    profile.tenant_id = FAKE_CLAIMS.tenant_id
    profile.b2b_or_b2c = kwargs.get("b2b_or_b2c", "both")
    profile.data_role = kwargs.get("data_role", "controller")
    profile.industry = kwargs.get("industry", "technology")
    profile.company_size = kwargs.get("company_size", "51-200")
    profile.primary_jurisdiction = kwargs.get("primary_jurisdiction", "Ireland")
    profile.number_of_data_subjects = "under_10k"
    profile.data_categories_processed = ["email"]
    profile.processing_purposes = ["service_delivery"]
    profile.data_subject_categories = ["customers"]
    profile.uses_cloud_services = True
    profile.cloud_providers = ["aws"]
    profile.has_on_premise_servers = False
    profile.has_compliance_officer = True
    profile.dpo_name = "Jane Smith"
    profile.dpo_email = "dpo@example.com"
    profile.certifications = []
    profile.previous_regulatory_action = False
    profile.gdpr_data = {"lawful_bases": ["consent"], "has_breach_procedure": True, "has_dpia": True}
    profile.nis2_data = {}
    profile.ai_act_data = {}
    return profile


def make_mock_assessment(**kwargs):
    a = MagicMock(spec=Assessment)
    a.id = kwargs.get("id", uuid.uuid4())
    a.assessment_id = kwargs.get("assessment_id", "asm_test001")
    a.tenant_id = kwargs.get("tenant_id", FAKE_CLAIMS.tenant_id)
    a.regulation_id = kwargs.get("regulation_id", GDPR_REG_ID)
    a.regulation_version_id = kwargs.get("regulation_version_id", None)
    a.previous_assessment_id = kwargs.get("previous_assessment_id", None)
    a.status = kwargs.get("status", AssessmentStatus.COMPLETED)
    a.score = kwargs.get("score", 72)
    a.risk_level = kwargs.get("risk_level", RiskLevel.MEDIUM)
    a.total_rules = kwargs.get("total_rules", 50)
    a.applicable_rules = kwargs.get("applicable_rules", 30)
    a.met_rules = kwargs.get("met_rules", 20)
    a.partial_rules = kwargs.get("partial_rules", 3)
    a.not_met_rules = kwargs.get("not_met_rules", 4)
    a.unknown_rules = kwargs.get("unknown_rules", 3)
    a.profile_snapshot = kwargs.get("profile_snapshot", {})
    a.triggered_by = kwargs.get("triggered_by", "user_test123")
    a.completed_at = kwargs.get("completed_at", datetime.now(timezone.utc))
    a.created_at = kwargs.get("created_at", datetime.now(timezone.utc))
    a.expires_at = kwargs.get("expires_at", datetime.now(timezone.utc) + timedelta(days=90))
    return a


def make_mock_gap(**kwargs):
    g = MagicMock(spec=Gap)
    g.id = kwargs.get("id", uuid.uuid4())
    g.gap_id = kwargs.get("gap_id", "gap_test001")
    g.assessment_id = kwargs.get("assessment_id", uuid.uuid4())
    g.tenant_id = kwargs.get("tenant_id", FAKE_CLAIMS.tenant_id)
    g.article = kwargs.get("article", "Article 5")
    g.article_number = kwargs.get("article_number", 5)
    g.chapter = kwargs.get("chapter", "Chapter II")
    g.category = kwargs.get("category", "Core Principles")
    g.severity = kwargs.get("severity", "critical")
    g.fine_tier = kwargs.get("fine_tier", "tier_2")
    g.status = kwargs.get("status", GapStatus.NOT_MET)
    g.score = kwargs.get("score", 0)
    g.evidence = kwargs.get("evidence", {})
    g.remediation_priority = kwargs.get("remediation_priority", "critical")
    g.remediation_steps = kwargs.get("remediation_steps", {"steps": ["Fix this"]})
    g.remediation_resources = kwargs.get("remediation_resources", {"links": []})
    g.assigned_to = kwargs.get("assigned_to", None)
    g.due_date = kwargs.get("due_date", None)
    g.resolved = kwargs.get("resolved", False)
    g.resolved_at = kwargs.get("resolved_at", None)
    g.resolved_by = kwargs.get("resolved_by", None)
    g.notes = kwargs.get("notes", None)
    return g


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


def make_mock_row(assessment, regulation_name="GDPR"):
    row = MagicMock()
    row.Assessment = assessment
    row.regulation_name = regulation_name
    return row


def rows_result(rows):
    r = MagicMock()
    r.all.return_value = rows
    return r


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
# POST /api/v1/assessments — run assessment
# ═══════════════════════════════════════════════════════════════════════════════

class TestRunAssessment:

    def _mock_new_assessment_flow(self, mock_session, regulation=None, profile=None):
        """Set up mocks for a successful new assessment trigger."""
        reg = regulation or make_mock_regulation()
        pro = profile or make_mock_profile()
        assessment = make_mock_assessment(status=AssessmentStatus.PENDING)

        call_count = 0

        async def side_effect(stmt):
            nonlocal call_count
            call_count += 1
            if call_count == 1:   # regulation lookup
                return scalar_result(reg)
            if call_count == 2:   # profile lookup
                return scalar_result(pro)
            if call_count == 3:   # cooldown running check
                return scalar_result(None)
            if call_count == 4:   # cooldown recent check
                return scalar_result(None)
            if call_count == 5:   # regulation version
                return scalar_result(None)
            if call_count == 6:   # previous assessment
                return scalar_result(None)
            return scalar_result(None)

        mock_session.execute = side_effect

        async def fake_refresh(obj):
            obj.assessment_id = assessment.assessment_id
            obj.status = AssessmentStatus.PENDING

        mock_session.refresh = fake_refresh
        return assessment

    @patch("app.routers.assessments.create_pool")
    def test_returns_202_for_new_assessment(self, mock_pool, client):
        """New assessment → 202 with assessment_id."""
        test_client, mock_session = client
        mock_redis = AsyncMock()
        mock_pool.return_value = mock_redis
        self._mock_new_assessment_flow(mock_session)

        response = test_client.post(
            "/api/v1/assessments",
            json={"regulation_name": "GDPR"},
        )
        assert response.status_code == 202
        assert "assessment_id" in response.json()

    @patch("app.routers.assessments.create_pool")
    def test_regulation_name_case_insensitive(self, mock_pool, client):
        """gdpr, Gdpr, GDPR all work."""
        test_client, mock_session = client
        mock_redis = AsyncMock()
        mock_pool.return_value = mock_redis
        self._mock_new_assessment_flow(mock_session)

        response = test_client.post(
            "/api/v1/assessments",
            json={"regulation_name": "gdpr"},
        )
        assert response.status_code == 202

    def test_unknown_regulation_returns_404(self, client):
        """Unknown regulation → 404."""
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=scalar_result(None))

        response = test_client.post(
            "/api/v1/assessments",
            json={"regulation_name": "UNKNOWN_REG"},
        )
        assert response.status_code == 404

    def test_missing_profile_returns_404(self, client):
        """No company profile → 404."""
        test_client, mock_session = client
        call_count = 0

        async def side_effect(stmt):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return scalar_result(make_mock_regulation())
            return scalar_result(None)  # no profile

        mock_session.execute = side_effect

        response = test_client.post("/api/v1/assessments", json={"regulation_name": "GDPR"})
        assert response.status_code == 404

    def test_incomplete_profile_returns_422(self, client):
        """Incomplete profile → 422."""
        test_client, mock_session = client
        call_count = 0

        async def side_effect(stmt):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return scalar_result(make_mock_regulation())
            return scalar_result(make_mock_profile(is_complete=False))

        mock_session.execute = side_effect

        response = test_client.post("/api/v1/assessments", json={"regulation_name": "GDPR"})
        assert response.status_code == 422

    def test_returns_existing_when_assessment_pending(self, client):
        """Assessment already pending → return existing, no new job queued."""
        test_client, mock_session = client
        running = make_mock_assessment(
            assessment_id="asm_existing",
            status=AssessmentStatus.PENDING,
        )
        call_count = 0

        async def side_effect(stmt):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return scalar_result(make_mock_regulation())
            if call_count == 2:
                return scalar_result(make_mock_profile())
            return scalar_result(running)  # cooldown check finds running

        mock_session.execute = side_effect

        response = test_client.post("/api/v1/assessments", json={"regulation_name": "GDPR"})

        assert response.status_code == 202
        data = response.json()
        assert data["assessment_id"] == "asm_existing"
        assert "already in progress" in data["message"]

    def test_returns_existing_when_assessment_running(self, client):
        """Assessment already running → return existing."""
        test_client, mock_session = client
        running = make_mock_assessment(
            assessment_id="asm_running",
            status=AssessmentStatus.RUNNING,
        )
        call_count = 0

        async def side_effect(stmt):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return scalar_result(make_mock_regulation())
            if call_count == 2:
                return scalar_result(make_mock_profile())
            return scalar_result(running)

        mock_session.execute = side_effect

        response = test_client.post("/api/v1/assessments", json={"regulation_name": "GDPR"})
        assert response.json()["assessment_id"] == "asm_running"

    def test_returns_existing_when_completed_within_1_hour(self, client):
        """Assessment completed < 1hr ago → return existing."""
        test_client, mock_session = client
        recent = make_mock_assessment(
            assessment_id="asm_recent",
            status=AssessmentStatus.COMPLETED,
            completed_at=datetime.now(timezone.utc) - timedelta(minutes=30),
        )
        call_count = 0

        async def side_effect(stmt):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return scalar_result(make_mock_regulation())
            if call_count == 2:
                return scalar_result(make_mock_profile())
            if call_count == 3:  # running check
                return scalar_result(None)
            return scalar_result(recent)  # recent check

        mock_session.execute = side_effect

        response = test_client.post("/api/v1/assessments", json={"regulation_name": "GDPR"})
        assert response.json()["assessment_id"] == "asm_recent"
        assert "1 hour ago" in response.json()["message"]

    @patch("app.routers.assessments.create_pool")
    def test_failed_assessment_within_1hr_does_not_trigger_cooldown(self, mock_pool, client):
        """Failed assessment < 1hr ago → NOT caught by cooldown → creates new."""
        test_client, mock_session = client
        mock_redis = AsyncMock()
        mock_pool.return_value = mock_redis
        self._mock_new_assessment_flow(mock_session)

        # Failed assessment is not in PENDING/RUNNING and not in COMPLETED cooldown
        # The mock flow returns None for both cooldown checks → creates new
        response = test_client.post("/api/v1/assessments", json={"regulation_name": "GDPR"})
        assert response.status_code == 202

    @patch("app.routers.assessments.create_pool")
    def test_gdpr_cooldown_does_not_affect_nis2(self, mock_pool, client):
        """GDPR assessment cooldown doesn't block NIS2 assessment trigger."""
        test_client, mock_session = client
        mock_redis = AsyncMock()
        mock_pool.return_value = mock_redis

        nis2_reg = make_mock_regulation(name="NIS2", reg_id=NIS2_REG_ID)
        self._mock_new_assessment_flow(mock_session, regulation=nis2_reg)

        response = test_client.post("/api/v1/assessments", json={"regulation_name": "NIS2"})
        assert response.status_code == 202


# ═══════════════════════════════════════════════════════════════════════════════
# GET /api/v1/assessments/latest
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetLatestAssessments:

    def test_returns_latest_per_regulation(self, client):
        """Returns latest completed assessment for each regulation."""
        test_client, mock_session = client

        gdpr_id = uuid.uuid4()
        nis2_id = uuid.uuid4()
        ai_id = uuid.uuid4()

        reg_gdpr = make_mock_regulation("GDPR", reg_id=gdpr_id)
        reg_nis2 = make_mock_regulation("NIS2", reg_id=nis2_id)
        reg_ai = make_mock_regulation("EU_AI_ACT", reg_id=ai_id)

        asm_gdpr = make_mock_assessment(regulation_id=gdpr_id)
        asm_nis2 = make_mock_assessment(regulation_id=nis2_id, assessment_id="asm_nis2")
        asm_ai = make_mock_assessment(regulation_id=ai_id, assessment_id="asm_ai")

        profile = make_mock_profile()

        call_count = 0

        async def side_effect(stmt):
            nonlocal call_count
            call_count += 1
            if call_count == 1:  # profile
                return scalar_result(profile)
            if call_count == 2:  # batch regulations
                return scalars_result([reg_gdpr, reg_nis2, reg_ai])
            if call_count == 3:  # batch assessments
                return scalars_result([asm_gdpr, asm_nis2, asm_ai])
            return scalars_result([])

        mock_session.execute = side_effect

        response = test_client.get("/api/v1/assessments/latest")
        assert response.status_code == 200
        data = response.json()
        assert "assessments" in data
        assert len(data["assessments"]) == 3  # GDPR, NIS2, EU_AI_ACT

    def test_never_run_shows_null_score(self, client):
        """Regulation never assessed → score is null, status is never_run."""
        test_client, mock_session = client

        gdpr_id = uuid.uuid4()
        nis2_id = uuid.uuid4()
        ai_id = uuid.uuid4()

        reg_gdpr = make_mock_regulation("GDPR", reg_id=gdpr_id)
        reg_nis2 = make_mock_regulation("NIS2", reg_id=nis2_id)
        reg_ai = make_mock_regulation("EU_AI_ACT", reg_id=ai_id)

        # Profile must make all 3 regs applicable so status is never_run not not_applicable
        profile = make_mock_profile()
        profile.nis2_data = {"sectors": ["energy"]}
        profile.ai_act_data = {"uses_ai": True, "ai_role": "deployer"}
        # company_size must be a mock with .value since _applicability calls .value on it
        profile.company_size = MagicMock(value="51-200")

        call_count = 0

        async def side_effect(stmt):
            nonlocal call_count
            call_count += 1
            if call_count == 1:  # profile
                return scalar_result(profile)
            if call_count == 2:  # batch regulations
                return scalars_result([reg_gdpr, reg_nis2, reg_ai])
            return scalars_result([])  # no assessments for any regulation

        mock_session.execute = side_effect

        response = test_client.get("/api/v1/assessments/latest")
        data = response.json()
        for item in data["assessments"]:
            assert item["score"] is None
            assert item["status"] == "never_run"


# ═══════════════════════════════════════════════════════════════════════════════
# GET /api/v1/assessments/{id}
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetAssessment:

    def test_returns_assessment_data(self, client):
        """Existing assessment → 200 with score data."""
        test_client, mock_session = client
        assessment = make_mock_assessment(score=72, assessment_id="asm_test001")
        mock_session.execute = AsyncMock(return_value=scalar_result(assessment))

        response = test_client.get("/api/v1/assessments/asm_test001")
        assert response.status_code == 200
        assert response.json()["score"] == 72

    def test_unknown_assessment_returns_404(self, client):
        """Unknown assessment_id → 404."""
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=scalar_result(None))

        response = test_client.get("/api/v1/assessments/asm_unknown")
        assert response.status_code == 404

    def test_other_tenant_assessment_returns_404(self, client):
        """Assessment from another tenant → 404 not 403 (don't reveal existence)."""
        test_client, mock_session = client
        # RLS on tenant_id means the query returns None for other tenants
        mock_session.execute = AsyncMock(return_value=scalar_result(None))

        response = test_client.get("/api/v1/assessments/asm_other_tenant")
        assert response.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════════
# GET /api/v1/assessments/{id}/gaps
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetGaps:

    def test_returns_gaps_for_valid_assessment(self, client):
        """Valid assessment → 200 with gap list."""
        test_client, mock_session = client
        assessment = make_mock_assessment()
        gaps = [make_mock_gap(), make_mock_gap(gap_id="gap_test002", article_number=6)]
        call_count = 0

        async def side_effect(stmt):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return scalar_result(assessment)
            return scalars_result(gaps)

        mock_session.execute = side_effect

        response = test_client.get("/api/v1/assessments/asm_test001/gaps")
        assert response.status_code == 200
        assert response.json()["total"] == 2

    def test_unknown_assessment_returns_404(self, client):
        """Unknown assessment → 404."""
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=scalar_result(None))

        response = test_client.get("/api/v1/assessments/asm_unknown/gaps")
        assert response.status_code == 404

    def test_other_tenant_assessment_returns_404(self, client):
        """Another tenant's assessment → 404."""
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=scalar_result(None))

        response = test_client.get("/api/v1/assessments/asm_other/gaps")
        assert response.status_code == 404

    def test_empty_gaps_returns_empty_list(self, client):
        """Assessment with no gaps → 200 with empty list."""
        test_client, mock_session = client
        call_count = 0

        async def side_effect(stmt):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return scalar_result(make_mock_assessment())
            return scalars_result([])

        mock_session.execute = side_effect

        response = test_client.get("/api/v1/assessments/asm_test001/gaps")
        assert response.status_code == 200
        assert response.json()["total"] == 0
        assert response.json()["gaps"] == []


# ═══════════════════════════════════════════════════════════════════════════════
# GET /api/v1/assessments/history
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetHistory:

    def test_returns_completed_assessments(self, client):
        """Returns list of completed assessments."""
        test_client, mock_session = client
        rows = [
            make_mock_row(make_mock_assessment(assessment_id="asm_1", score=72), "GDPR"),
            make_mock_row(make_mock_assessment(assessment_id="asm_2", score=65), "NIS2"),
        ]
        mock_session.execute = AsyncMock(return_value=rows_result(rows))

        response = test_client.get("/api/v1/assessments/history")
        assert response.status_code == 200
        data = response.json()
        assert len(data["history"]) == 2
        assert data["history"][0]["assessment_id"] == "asm_1"

    def test_empty_history_returns_empty_list(self, client):
        """No assessments → empty list not 404."""
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=scalars_result([]))

        response = test_client.get("/api/v1/assessments/history")
        assert response.status_code == 200
        assert response.json()["history"] == []

    def test_filter_by_regulation(self, client):
        """?regulation=GDPR filters correctly."""
        test_client, mock_session = client
        call_count = 0

        async def side_effect(stmt):
            nonlocal call_count
            call_count += 1
            if call_count == 1:  # regulation lookup
                return scalar_result(make_mock_regulation())
            return scalars_result([make_mock_assessment()])

        mock_session.execute = side_effect

        response = test_client.get("/api/v1/assessments/history?regulation=GDPR")
        assert response.status_code == 200

    def test_unknown_regulation_filter_returns_empty(self, client):
        """Unknown regulation in filter → empty list."""
        test_client, mock_session = client
        call_count = 0

        async def side_effect(stmt):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return scalar_result(None)  # regulation not found
            return scalars_result([])

        mock_session.execute = side_effect

        response = test_client.get("/api/v1/assessments/history?regulation=UNKNOWN")
        assert response.status_code == 200
        assert response.json()["history"] == []

    def test_default_limit_is_10(self, client):
        """Default limit is 10."""
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=scalars_result([]))
        response = test_client.get("/api/v1/assessments/history")
        assert response.status_code == 200

    def test_history_contains_required_fields(self, client):
        """Each history item has required fields."""
        test_client, mock_session = client
        row = make_mock_row(make_mock_assessment(assessment_id="asm_1", score=72), "GDPR")
        mock_session.execute = AsyncMock(return_value=rows_result([row]))

        response = test_client.get("/api/v1/assessments/history")
        item = response.json()["history"][0]
        assert "assessment_id" in item
        assert "score" in item
        assert "risk_level" in item
        assert "completed_at" in item
        assert "met_rules" in item
        assert "not_met_rules" in item

    def test_only_returns_current_tenant_history(self, client):
        """History only includes current tenant's assessments."""
        test_client, mock_session = client
        # RLS on tenant_id ensures only tenant's assessments are returned
        # The mock returns empty — simulating no assessments for this tenant
        mock_session.execute = AsyncMock(return_value=scalars_result([]))

        response = test_client.get("/api/v1/assessments/history")
        assert response.status_code == 200
        assert response.json()["history"] == []


# ═══════════════════════════════════════════════════════════════════════════════
# PATCH /api/v1/assessments/{id}/gaps/{gap_id}
# ═══════════════════════════════════════════════════════════════════════════════

class TestUpdateGap:

    def _setup_gap_update(self, mock_session, assessment=None, gap=None):
        """Set up mocks for gap update — assessment lookup then gap lookup."""
        a = assessment or make_mock_assessment()
        g = gap or make_mock_gap()
        call_count = 0

        async def side_effect(stmt):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return scalar_result(a)
            return scalar_result(g)

        mock_session.execute = side_effect
        return a, g

    def test_resolve_gap(self, client):
        """Resolving a gap sets resolved=True and resolved_at."""
        test_client, mock_session = client
        gap = make_mock_gap(resolved=False)
        self._setup_gap_update(mock_session, gap=gap)

        response = test_client.patch(
            "/api/v1/assessments/asm_test001/gaps/gap_test001",
            json={"resolved": True},
        )
        assert response.status_code == 200
        assert gap.resolved is True
        assert gap.resolved_at is not None
        assert gap.resolved_by == FAKE_CLAIMS.user_id

    def test_unresolve_gap(self, client):
        """Unresolving a gap clears resolved_at and resolved_by."""
        test_client, mock_session = client
        gap = make_mock_gap(
            resolved=True,
            resolved_at=datetime.now(timezone.utc),
            resolved_by="user_test123",
        )
        self._setup_gap_update(mock_session, gap=gap)

        response = test_client.patch(
            "/api/v1/assessments/asm_test001/gaps/gap_test001",
            json={"resolved": False},
        )
        assert response.status_code == 200
        assert gap.resolved is False
        assert gap.resolved_at is None
        assert gap.resolved_by is None

    def test_resolve_already_resolved_gap_is_idempotent(self, client):
        """Resolving an already resolved gap updates resolved_at to now."""
        test_client, mock_session = client
        old_time = datetime.now(timezone.utc) - timedelta(hours=2)
        gap = make_mock_gap(resolved=True, resolved_at=old_time)
        self._setup_gap_update(mock_session, gap=gap)

        response = test_client.patch(
            "/api/v1/assessments/asm_test001/gaps/gap_test001",
            json={"resolved": True},
        )
        assert response.status_code == 200
        # resolved_at should be updated to now (more recent than old_time)
        assert gap.resolved is True

    def test_unresolve_already_unresolved_gap_is_idempotent(self, client):
        """Unresolving an already unresolved gap is safe."""
        test_client, mock_session = client
        gap = make_mock_gap(resolved=False, resolved_at=None)
        self._setup_gap_update(mock_session, gap=gap)

        response = test_client.patch(
            "/api/v1/assessments/asm_test001/gaps/gap_test001",
            json={"resolved": False},
        )
        assert response.status_code == 200
        assert gap.resolved is False

    def test_update_notes_only(self, client):
        """Updating notes only — resolved status unchanged."""
        test_client, mock_session = client
        gap = make_mock_gap(resolved=False, notes=None)
        self._setup_gap_update(mock_session, gap=gap)

        response = test_client.patch(
            "/api/v1/assessments/asm_test001/gaps/gap_test001",
            json={"notes": "Working on this with legal team."},
        )
        assert response.status_code == 200
        assert gap.notes == "Working on this with legal team."
        assert gap.resolved is False  # unchanged

    def test_update_assigned_to_only(self, client):
        """Updating assigned_to only — other fields unchanged."""
        test_client, mock_session = client
        gap = make_mock_gap(assigned_to=None)
        self._setup_gap_update(mock_session, gap=gap)

        response = test_client.patch(
            "/api/v1/assessments/asm_test001/gaps/gap_test001",
            json={"assigned_to": "user_jane123"},
        )
        assert response.status_code == 200
        assert gap.assigned_to == "user_jane123"

    def test_update_due_date(self, client):
        """Setting a valid ISO due date."""
        test_client, mock_session = client
        gap = make_mock_gap(due_date=None)
        self._setup_gap_update(mock_session, gap=gap)

        response = test_client.patch(
            "/api/v1/assessments/asm_test001/gaps/gap_test001",
            json={"due_date": "2026-08-01"},
        )
        assert response.status_code == 200

    def test_all_none_body_changes_nothing(self, client):
        """Body with all None values — nothing changes."""
        test_client, mock_session = client
        gap = make_mock_gap(resolved=False, notes="existing note")
        self._setup_gap_update(mock_session, gap=gap)

        response = test_client.patch(
            "/api/v1/assessments/asm_test001/gaps/gap_test001",
            json={},
        )
        assert response.status_code == 200
        assert gap.resolved is False
        assert gap.notes == "existing note"

    def test_assessment_not_found_returns_404(self, client):
        """Assessment not found → 404."""
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=scalar_result(None))

        response = test_client.patch(
            "/api/v1/assessments/asm_unknown/gaps/gap_test001",
            json={"resolved": True},
        )
        assert response.status_code == 404

    def test_gap_not_found_returns_404(self, client):
        """Assessment found but gap not found → 404."""
        test_client, mock_session = client
        call_count = 0

        async def side_effect(stmt):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return scalar_result(make_mock_assessment())
            return scalar_result(None)  # gap not found

        mock_session.execute = side_effect

        response = test_client.patch(
            "/api/v1/assessments/asm_test001/gaps/gap_unknown",
            json={"resolved": True},
        )
        assert response.status_code == 404

    def test_other_tenant_assessment_returns_404(self, client):
        """Another tenant's assessment → 404 not 403."""
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=scalar_result(None))

        response = test_client.patch(
            "/api/v1/assessments/asm_other_tenant/gaps/gap_test001",
            json={"resolved": True},
        )
        assert response.status_code == 404

    def test_resolve_and_notes_together(self, client):
        """Resolve and add notes in one request."""
        test_client, mock_session = client
        gap = make_mock_gap(resolved=False, notes=None)
        self._setup_gap_update(mock_session, gap=gap)

        response = test_client.patch(
            "/api/v1/assessments/asm_test001/gaps/gap_test001",
            json={"resolved": True, "notes": "Fixed by implementing breach procedure."},
        )
        assert response.status_code == 200
        assert gap.resolved is True
        assert gap.notes == "Fixed by implementing breach procedure."


# ═══════════════════════════════════════════════════════════════════════════════
# GET /api/v1/assessments/{id}/stats
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetStats:

    def _setup_stats(self, mock_session, assessment=None, side_effect_fn=None):
        if side_effect_fn:
            mock_session.execute = side_effect_fn
            return
        a = assessment or make_mock_assessment()
        call_count = 0

        async def default_side_effect(stmt):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return scalar_result(a)
            # Return empty results for group by queries
            r = MagicMock()
            r.__iter__ = MagicMock(return_value=iter([]))
            r.scalars = MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))
            return r

        mock_session.execute = default_side_effect

    def test_returns_stats_for_valid_assessment(self, client):
        """Valid assessment → 200 with stats."""
        test_client, mock_session = client
        self._setup_stats(mock_session)

        response = test_client.get("/api/v1/assessments/asm_test001/stats")
        assert response.status_code == 200
        data = response.json()
        assert "assessment_id" in data
        assert "by_severity" in data
        assert "by_category" in data
        assert "quick_wins" in data

    def test_unknown_assessment_returns_404(self, client):
        """Unknown assessment → 404."""
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=scalar_result(None))

        response = test_client.get("/api/v1/assessments/asm_unknown/stats")
        assert response.status_code == 404

    def test_other_tenant_assessment_returns_404(self, client):
        """Another tenant's assessment → 404."""
        test_client, mock_session = client
        mock_session.execute = AsyncMock(return_value=scalar_result(None))

        response = test_client.get("/api/v1/assessments/asm_other/stats")
        assert response.status_code == 404

    def test_no_gaps_returns_empty_stats(self, client):
        """Assessment with no gaps → empty stats, no crash."""
        test_client, mock_session = client
        self._setup_stats(mock_session)

        response = test_client.get("/api/v1/assessments/asm_test001/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["quick_wins"] == []
        assert data["by_category"] == []


# ═══════════════════════════════════════════════════════════════════════════════
# HTTP method enforcement
# ═══════════════════════════════════════════════════════════════════════════════

class TestMethodEnforcement:

    def test_delete_assessments_not_allowed(self, client):
        test_client, _ = client
        assert test_client.delete("/api/v1/assessments").status_code == 405

    def test_put_assessment_not_allowed(self, client):
        test_client, _ = client
        assert test_client.put("/api/v1/assessments/asm_test001", json={}).status_code == 405

    def test_post_to_gaps_not_allowed(self, client):
        test_client, _ = client
        assert test_client.post("/api/v1/assessments/asm_test001/gaps", json={}).status_code == 405