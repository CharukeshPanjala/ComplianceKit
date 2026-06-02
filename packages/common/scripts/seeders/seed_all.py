"""
Run all regulation seeders in order.
Run locally:
  cd packages/common && DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/compliancekit \
    uv run python scripts/seeders/seed_all.py
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from scripts.seeders.seed_gdpr import seed as seed_gdpr
from scripts.seeders.seed_nis2 import seed as seed_nis2
from scripts.seeders.seed_eu_ai_act import seed as seed_eu_ai_act


async def seed_all() -> None:
    print("── Seeding all regulations ──────────────────")
    await seed_gdpr()
    await seed_nis2()
    await seed_eu_ai_act()
    print("── All regulations seeded ✅ ─────────────────")


if __name__ == "__main__":
    asyncio.run(seed_all())