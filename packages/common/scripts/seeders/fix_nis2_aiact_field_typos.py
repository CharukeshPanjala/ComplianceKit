"""
One-off correction script — fixes typo'd field names in already-seeded
NIS2 and EU AI Act rows' `profile_field` / `evaluation_logic` columns
(see docs/article_audit_nis2.md, docs/article_audit_ai_act.md).

Confirmed these typos do NOT affect live scoring — services/policy-engine/app/engine/scorer.py
dispatches on check_type + article_number with hardcoded Python and already uses the
correct field names. This is a metadata/data-integrity fix only.

Typo -> correct:
  nis2_data.nis2_sectors        -> nis2_data.sectors
  nis2_data.has_incident_plan   -> nis2_data.has_incident_response_plan
  ai_act_data.high_risk_categories -> ai_act_data.high_risk_ai_categories
  ai_act_data.role               -> ai_act_data.ai_role
  ai_act_data.gpai_model          -> ai_act_data.uses_gpai

Run inside Docker:
  docker compose -f infrastructure/docker/docker-compose.yml exec api-gateway \
    uv run python /app/packages/common/scripts/seeders/fix_nis2_aiact_field_typos.py
"""
import asyncio
import json
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

REPLACEMENTS = {
    "NIS2": [
        ("nis2_data.nis2_sectors", "nis2_data.sectors"),
        ("nis2_data.has_incident_plan", "nis2_data.has_incident_response_plan"),
    ],
    "EU_AI_ACT": [
        ("ai_act_data.high_risk_categories", "ai_act_data.high_risk_ai_categories"),
        ("ai_act_data.role", "ai_act_data.ai_role"),
        ("ai_act_data.gpai_model", "ai_act_data.uses_gpai"),
    ],
}


def _replace_in_value(value: str, replacements: list[tuple[str, str]]) -> str:
    for old, new in replacements:
        value = value.replace(old, new)
    return value


async def fix() -> None:
    async with SessionLocal() as session:
        total_fixed = 0
        for reg_name, replacements in REPLACEMENTS.items():
            reg = await session.scalar(select(Regulation).where(Regulation.name == reg_name))
            if not reg:
                print(f"{reg_name} not seeded — skipping.")
                continue

            rules = (await session.scalars(select(Rule).where(Rule.regulation_id == reg.id))).all()
            for rule in rules:
                changed = False

                if rule.profile_field:
                    new_field = _replace_in_value(rule.profile_field, replacements)
                    if new_field != rule.profile_field:
                        rule.profile_field = new_field
                        changed = True

                if rule.evaluation_logic:
                    raw = json.dumps(rule.evaluation_logic)
                    new_raw = _replace_in_value(raw, replacements)
                    if new_raw != raw:
                        rule.evaluation_logic = json.loads(new_raw)
                        changed = True

                if changed:
                    total_fixed += 1
                    print(f"✓ Fixed {reg_name} {rule.article}")

        await session.commit()
        print(f"✅ {total_fixed} rule rows corrected.")


if __name__ == "__main__":
    asyncio.run(fix())
