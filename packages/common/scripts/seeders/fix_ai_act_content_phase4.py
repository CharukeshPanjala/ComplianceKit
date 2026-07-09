"""
Phase 4 content fix — applies the 44 corrected article contents + 1 new
article (Article 54, "Authorised representatives of providers of GPAI
models") to the already-seeded EU AI Act rows. See docs/article_audit_ai_act.md
and docs/ai_act_content_corrections.md for the full rationale.

One-off correction script: the seeders are insert-only and skip if the
regulation already exists, so already-seeded rows must be patched directly.
Reads EU_AI_ACT_ARTICLES from seed_eu_ai_act.py as the source of truth so
this script can never drift out of sync with the seed file.

Run inside Docker:
  docker compose -f infrastructure/docker/docker-compose.yml exec api-gateway \
    uv run python /app/packages/common/scripts/seeders/fix_ai_act_content_phase4.py
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
from common.utils.ids import generate_rule_id
from scripts.seeders.seed_eu_ai_act import EU_AI_ACT_ARTICLES

settings = BaseServiceSettings()
engine = create_async_engine(settings.database_url, echo=False)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

CONTENT_FIELDS = ("title", "description", "plain_english", "chapter")


async def fix() -> None:
    async with SessionLocal() as session:
        reg = await session.scalar(select(Regulation).where(Regulation.name == "EU_AI_ACT"))
        if not reg:
            print("EU_AI_ACT not seeded — nothing to fix.")
            return

        updated = 0
        inserted = 0

        for article in EU_AI_ACT_ARTICLES:
            article_number = article["article_number"]
            rule = await session.scalar(
                select(Rule).where(
                    Rule.regulation_id == reg.id,
                    Rule.article_number == article_number,
                )
            )

            if rule is None:
                # New article (Article 54) — insert full row from seed data
                session.add(
                    Rule(
                        rule_id=generate_rule_id(),
                        regulation_id=reg.id,
                        article=article["article"],
                        article_number=article["article_number"],
                        title=article.get("title"),
                        chapter=article.get("chapter"),
                        category=article.get("category"),
                        description=article["description"],
                        plain_english=article.get("plain_english"),
                        severity=article["severity"],
                        profile_field=article.get("profile_field"),
                        evaluation_logic=article.get("evaluation_logic"),
                        remediation_hint=article.get("remediation_hint"),
                        applicability_tags=article.get("applicability_tags", []),
                        applies_to_b2c=article.get("applies_to_b2c", True),
                        applies_to_b2b=article.get("applies_to_b2b", True),
                        fine_tier=article.get("fine_tier"),
                        is_mandatory=article.get("is_mandatory", True),
                        check_type=article.get("check_type", "informational"),
                    )
                )
                inserted += 1
                print(f"+ Inserted Article {article_number}")
                continue

            changed = False
            for field in CONTENT_FIELDS:
                new_value = article.get(field)
                if new_value is not None and getattr(rule, field) != new_value:
                    setattr(rule, field, new_value)
                    changed = True

            if changed:
                updated += 1
                print(f"✓ Updated Article {article_number}")

        await session.commit()
        print(f"✅ {updated} rows updated, {inserted} rows inserted.")


if __name__ == "__main__":
    asyncio.run(fix())
