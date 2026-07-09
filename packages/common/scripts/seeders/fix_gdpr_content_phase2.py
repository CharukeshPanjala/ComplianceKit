"""
Phase 2 content fix — corrects 3 already-seeded GDPR rows whose
evaluation_logic / plain_english text was wrong (see docs/article_audit_gdpr.md).

One-off correction script: the seeders are insert-only and skip if the
regulation already exists, so already-seeded rows must be patched directly.
Run inside Docker:
  docker compose -f infrastructure/docker/docker-compose.yml exec api-gateway \
    uv run python /app/packages/common/scripts/seeders/fix_gdpr_content_phase2.py
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

FIXES = {
    26: {
        "evaluation_logic": {
            "type": "document_required",
            "note": "no profile field exists yet to detect joint-controller status; requires manual or document review",
            "required_documents": ["joint_controller_agreement"],
        },
    },
    37: {
        "evaluation_logic": {
            "type": "profile_field",
            "check": "has_compliance_officer == true",
            "fields": ["has_compliance_officer"],
            "limitation": (
                "DPO-mandatory triggers (public authority, large-scale monitoring, "
                "large-scale special-category processing) are not independently computed; "
                "no `is_public_authority` field exists yet, so the engine can only check "
                "whether a DPO exists, not whether one is legally required"
            ),
        },
    },
    58: {
        "plain_english": (
            "Supervisory authorities can audit you, order you to stop processing, "
            "and impose fines (see Article 83 for the exact amounts)."
        ),
    },
}


async def fix() -> None:
    async with SessionLocal() as session:
        reg = await session.scalar(select(Regulation).where(Regulation.name == "GDPR"))
        if not reg:
            print("GDPR not seeded — nothing to fix.")
            return

        for article_number, fields in FIXES.items():
            rule = await session.scalar(
                select(Rule).where(
                    Rule.regulation_id == reg.id,
                    Rule.article_number == article_number,
                )
            )
            if not rule:
                print(f"Article {article_number} not found — skipping.")
                continue
            for key, value in fields.items():
                setattr(rule, key, value)
            print(f"✓ Fixed Article {article_number}")

        await session.commit()
        print("✅ GDPR Phase 2 content fixes applied.")


if __name__ == "__main__":
    asyncio.run(fix())
