"""
Phase 7 content fix — correct article titles, check_types, and profile_fields
across GDPR (2 rows), NIS2 (15 rows), and EU AI Act (15 rows).

One-off correction script: the seeders are insert-only and skip if the
regulation already exists, so already-seeded rows must be patched directly.
Run inside Docker (api-gateway or policy-engine container):
  docker compose -f infrastructure/docker/docker-compose.yml exec api-gateway \
    uv run python /app/packages/common/scripts/seeders/fix_article_titles_phase7.py
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from common.config import BaseServiceSettings
from common.models.regulation import Regulation
from common.models.rule import Rule

settings = BaseServiceSettings()
engine = create_async_engine(settings.database_url, echo=False)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

GDPR_FIXES: dict[int, dict] = {
    19: {
        "title": "Notification obligation regarding rectification or erasure of personal data or restriction of processing",
    },
    22: {
        "profile_field": "gdpr_data.uses_automated_decisions",
        "evaluation_logic": {
            "type": "conditional",
            "condition": "gdpr_data.uses_automated_decisions == true",
            "then": "human_review_mechanism_documented",
        },
    },
}

NIS2_FIXES: dict[int, dict] = {
    8: {"title": "Single points of contact and role of ENISA"},
    9: {"title": "National cybersecurity strategies"},
    10: {"title": "Computer security incident response teams (CSIRTs)"},
    11: {"title": "Requirements, technical capabilities and tasks of CSIRTs"},
    12: {
        "check_type": "profile_field",
        "profile_field": "nis2_data.has_vulnerability_disclosure_policy",
        "evaluation_logic": {
            "type": "profile_field",
            "check": "nis2_data.has_vulnerability_disclosure_policy",
        },
    },
    13: {"title": "National-level cooperation"},
    14: {"title": "Cooperation Group"},
    16: {"title": "European cyber crises liaison organisation network (EU-CyCLONe)"},
    20: {
        "check_type": "profile_field",
        "profile_field": "nis2_data.management_approved_security_measures",
        "evaluation_logic": {
            "type": "profile_field",
            "check": "nis2_data.management_approved_security_measures",
        },
    },
    21: {
        "check_type": "profile_field",
        "profile_field": "nis2_data.has_mfa",
        "evaluation_logic": {
            "type": "profile_field",
            "check": "nis2_data.has_mfa",
        },
    },
    24: {
        "check_type": "profile_field",
        "profile_field": "nis2_data.uses_certified_products",
        "evaluation_logic": {
            "type": "profile_field",
            "check": "nis2_data.uses_certified_products",
        },
    },
    27: {
        "title": "Register of entities",
        "check_type": "profile_field",
        "profile_field": "nis2_data.nis2_registration_complete",
        "evaluation_logic": {
            "type": "profile_field",
            "check": "nis2_data.nis2_registration_complete",
        },
    },
    29: {
        "check_type": "profile_field",
        "profile_field": "nis2_data.participates_in_info_sharing",
        "evaluation_logic": {
            "type": "profile_field",
            "check": "nis2_data.participates_in_info_sharing",
        },
    },
    34: {
        "title": "General conditions for imposing administrative fines on essential and important entities",
    },
    35: {"title": "Infringements involving a personal data breach"},
}

EU_AI_ACT_FIXES: dict[int, dict] = {
    22: {"title": "Authorised representatives of providers of high-risk AI systems"},
    24: {"title": "Obligations of distributors"},
    45: {"title": "Information obligations of notified bodies"},
    48: {"title": "CE marking"},
    50: {
        "title": "Transparency obligations for providers and deployers of certain AI systems",
        "check_type": "profile_field",
        "profile_field": "ai_act_data.uses_chatbot",
        "evaluation_logic": {
            "type": "profile_field",
            "check": "ai_act_data.uses_chatbot OR ai_act_data.uses_synthetic_content OR ai_act_data.uses_emotion_recognition",
        },
    },
    51: {"title": "Classification of general-purpose AI models as general-purpose AI models with systemic risk"},
    55: {"title": "Obligations of providers of general-purpose AI models with systemic risk"},
    58: {"title": "Detailed arrangements for, and functioning of, AI regulatory sandboxes"},
    70: {"title": "Designation of national competent authorities and single points of contact"},
    71: {"title": "EU database for high-risk AI systems listed in Annex III"},
    73: {"title": "Reporting of serious incidents"},
    74: {"title": "Market surveillance and control of AI systems in the Union market"},
    75: {"title": "Mutual assistance, market surveillance and control of general-purpose AI systems"},
    86: {
        "title": "Right to explanation of individual decision-making",
        "check_type": "profile_field",
        "profile_field": "ai_act_data.has_ai_explanation_process",
        "evaluation_logic": {
            "type": "profile_field",
            "check": "ai_act_data.has_ai_explanation_process",
        },
    },
    87: {"title": "Reporting of infringements and protection of reporting persons"},
}


async def apply_fixes(
    session: AsyncSession,
    regulation_name: str,
    fixes: dict[int, dict],
) -> int:
    reg = await session.scalar(select(Regulation).where(Regulation.name == regulation_name))
    if not reg:
        print(f"  {regulation_name} not seeded — skipping.")
        return 0

    count = 0
    for article_number, fields in fixes.items():
        rule = await session.scalar(
            select(Rule).where(
                Rule.regulation_id == reg.id,
                Rule.article_number == article_number,
            )
        )
        if not rule:
            print(f"  Art. {article_number} not found — skipping.")
            continue
        for key, value in fields.items():
            setattr(rule, key, value)
        print(f"  ✓ {regulation_name} Art. {article_number}")
        count += 1

    return count


async def fix() -> None:
    async with SessionLocal() as session:
        total = 0

        print("\n── GDPR ─────────────────────────────────────────")
        total += await apply_fixes(session, "GDPR", GDPR_FIXES)

        print("\n── NIS2 ─────────────────────────────────────────")
        total += await apply_fixes(session, "NIS2", NIS2_FIXES)

        print("\n── EU_AI_ACT ────────────────────────────────────")
        total += await apply_fixes(session, "EU_AI_ACT", EU_AI_ACT_FIXES)

        await session.commit()
        print(f"\n✅ Phase 7 fixes applied — {total} rows updated.")


if __name__ == "__main__":
    asyncio.run(fix())
