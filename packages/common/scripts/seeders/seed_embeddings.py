"""
Seed vector embeddings for all 258 regulation rules.

Run via:  make seed-embeddings
Or:  cd packages/common && DATABASE_URL=... uv run python scripts/seeders/seed_embeddings.py

Idempotent — skips rules that already have an embedding.
Requires AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY to be set.
"""
import asyncio
import time

from sqlalchemy import select, update

from common.ai.client import get_async_client
from common.config import AIServiceSettings
from common.db.session import AdminSessionLocal
from common.models.rule import Rule

BATCH_SIZE = 20
BATCH_DELAY_SECONDS = 1.0


def build_rule_text(rule: Rule) -> str:
    parts = [rule.article or ""]
    if rule.title:
        parts.append(f": {rule.title}")
    parts.append(f"\n{rule.description}")
    if rule.plain_english:
        parts.append(f"\nPlain English: {rule.plain_english}")
    if rule.remediation_hint:
        parts.append(f"\nRemediation: {rule.remediation_hint}")
    return "".join(parts)


async def main() -> None:
    settings = AIServiceSettings()

    if not settings.ai_enabled:
        print("AI not configured — set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY in .env")
        return

    async with AdminSessionLocal() as session:
        result = await session.execute(
            select(Rule)
            .where(Rule.embedding.is_(None))
            .where(Rule.is_active.is_(True))
            .order_by(Rule.article)
        )
        rules = list(result.scalars().all())

    if not rules:
        print("All rules already have embeddings — nothing to do.")
        return

    total = len(rules)
    total_batches = (total + BATCH_SIZE - 1) // BATCH_SIZE
    print(f"Embedding {total} rules in {total_batches} batches of {BATCH_SIZE}...")

    client = get_async_client(settings)
    embedded = 0
    failed = 0

    for batch_num, i in enumerate(range(0, total, BATCH_SIZE), start=1):
        batch = rules[i : i + BATCH_SIZE]
        texts = [build_rule_text(r) for r in batch]

        try:
            resp = await client.embeddings.create(
                model=settings.azure_openai_deployment_embeddings,
                input=texts,
            )
        except Exception as exc:
            print(f"  Batch {batch_num}/{total_batches} FAILED: {exc}")
            failed += len(batch)
            continue

        vectors = [item.embedding for item in resp.data]

        async with AdminSessionLocal() as session:
            async with session.begin():
                for rule, vector in zip(batch, vectors):
                    await session.execute(
                        update(Rule).where(Rule.id == rule.id).values(embedding=vector)
                    )

        embedded += len(batch)
        print(f"  Batch {batch_num}/{total_batches} done — {embedded}/{total} rules embedded")

        if i + BATCH_SIZE < total:
            time.sleep(BATCH_DELAY_SECONDS)

    print(f"\nDone. {embedded} embedded, {failed} failed.")


if __name__ == "__main__":
    asyncio.run(main())
