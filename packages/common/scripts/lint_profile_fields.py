"""
Phase 6 guardrail — lints every profile_field value in seed files against the
known valid field paths. Fails with exit code 1 if any dangling references are
found so this class of typo cannot silently ship.

Run from repo root:
  uv run python packages/common/scripts/lint_profile_fields.py

Or in CI:
  python packages/common/scripts/lint_profile_fields.py
"""
import ast
import sys
from pathlib import Path

# ── Valid field paths ────────────────────────────────────────────────────────
# Top-level CompanyProfile fields (from services/api-gateway/app/api/v1/schemas/profile.py)
TOP_LEVEL = {
    "industry", "company_size", "b2b_or_b2c", "number_of_data_subjects",
    "data_role", "website_url", "primary_jurisdiction", "uses_cloud_services",
    "cloud_providers", "primary_cloud_region", "has_on_premise_servers",
    "certifications", "has_compliance_officer", "dpo_name", "dpo_email",
    "legal_contact_email", "previous_regulatory_action", "data_categories_processed",
    "processing_purposes", "data_subject_categories", "tech_stack",
    "gdpr_data", "nis2_data", "ai_act_data",
}

# gdpr_data sub-keys (from scorer._score_gdpr_field + Step6Form)
GDPR_KEYS = {
    "lawful_bases", "processes_children_data", "transfers_outside_eea",
    "transfer_mechanisms", "uses_data_processors", "has_breach_procedure",
    "has_dpia", "has_erasure_process", "has_restriction_process",
    "has_portability_process", "has_marketing_objection_process",
    "uses_automated_decisions", "has_joint_controllers", "is_public_authority",
    "processes_employee_data", "processes_for_research", "special_category_condition",
    "transfer_destination_countries", "derogation_types", "has_bcr",
    "has_public_incident_notification",
}

# nis2_data sub-keys (from scorer._score_nis2_field + Step6Form)
NIS2_KEYS = {
    "sectors", "entity_type", "has_mfa", "has_incident_response_plan",
    "has_business_continuity_plan", "assesses_supply_chain",
    "has_vulnerability_disclosure_policy", "management_approved_security_measures",
    "has_cyber_awareness_training", "uses_encryption", "has_asset_inventory",
    "participates_in_info_sharing", "uses_certified_products",
    "nis2_registration_complete", "has_public_incident_notification",
}

# ai_act_data sub-keys (from scorer._score_ai_act_field + Step6Form)
AI_ACT_KEYS = {
    "uses_ai", "ai_role", "high_risk_ai_categories", "uses_gpai",
    "has_ai_governance_policy", "has_ai_literacy_training", "is_public_body",
    "uses_chatbot", "uses_synthetic_content", "uses_emotion_recognition",
    "has_ai_complaint_process", "has_ai_explanation_process",
    "prohibited_practice_flags", "gpai_flops_above_threshold",
    "has_gpai_eu_representative",
}

JSONB_KEYS: dict[str, set[str]] = {
    "gdpr_data": GDPR_KEYS,
    "nis2_data": NIS2_KEYS,
    "ai_act_data": AI_ACT_KEYS,
}


def is_valid(field: str) -> bool:
    """Return True if the field path is a known valid profile reference."""
    if not field:
        return True
    parts = field.split(".", 1)
    root = parts[0]
    if root not in TOP_LEVEL:
        return False
    if len(parts) == 1:
        return True
    sub = parts[1]
    allowed_subs = JSONB_KEYS.get(root)
    if allowed_subs is None:
        return False
    return sub in allowed_subs


def extract_profile_fields_from_seed(path: Path) -> list[tuple[int, str]]:
    """Extract (line_number, field_value) for every profile_field string in the seed file."""
    source = path.read_text()
    tree = ast.parse(source)
    results: list[tuple[int, str]] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue
        for key, value in zip(node.keys, node.values):
            if not isinstance(key, ast.Constant) or key.value != "profile_field":
                continue
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                results.append((value.lineno, value.value))
            elif isinstance(value, ast.Constant) and value.value is None:
                pass  # None is valid (no profile field for this rule)

    return results


def main() -> int:
    repo_root = Path(__file__).resolve().parents[3]
    seed_dir = repo_root / "packages" / "common" / "scripts" / "seeders"

    seed_files = [
        seed_dir / "seed_gdpr.py",
        seed_dir / "seed_nis2.py",
        seed_dir / "seed_eu_ai_act.py",
    ]

    errors: list[str] = []

    for seed_file in seed_files:
        if not seed_file.exists():
            print(f"WARN: {seed_file} not found — skipping")
            continue

        fields = extract_profile_fields_from_seed(seed_file)
        for lineno, field in fields:
            if not is_valid(field):
                errors.append(f"{seed_file.name}:{lineno}: invalid profile_field '{field}'")

    if errors:
        print("❌ Dangling profile_field references found:")
        for e in errors:
            print(f"  {e}")
        print(
            "\nFix: ensure the field path matches a real key in ProfileCreate "
            "(top-level) or the JSONB sub-key allowlists in this script."
        )
        return 1

    print(f"✅ All profile_field references valid across {len(seed_files)} seed files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
