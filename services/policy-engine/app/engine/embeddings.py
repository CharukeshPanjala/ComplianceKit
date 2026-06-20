from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from common.ai.client import get_async_client
from common.config import AIServiceSettings
from common.models.rule import Rule


def build_rule_text(rule: Rule) -> str:
    """Combine rule fields into a single string for embedding."""
    parts = [rule.article or ""]
    if rule.title:
        parts.append(f": {rule.title}")
    parts.append(f"\n{rule.description}")
    if rule.plain_english:
        parts.append(f"\nPlain English: {rule.plain_english}")
    if rule.remediation_hint:
        parts.append(f"\nRemediation: {rule.remediation_hint}")
    return "".join(parts)


async def embed_text(text: str, settings: AIServiceSettings) -> list[float]:
    """Embed a single string via Azure OpenAI."""
    client = get_async_client(settings)
    resp = await client.embeddings.create(
        model=settings.azure_openai_deployment_embeddings,
        input=text,
    )
    return resp.data[0].embedding


async def search_rules(
    query: str,
    session: AsyncSession,
    settings: AIServiceSettings,
    top_k: int = 5,
    regulation_id: uuid.UUID | None = None,
) -> list[Rule]:
    """
    Embed query and return top-k most similar rules via cosine distance.
    Requires embeddings to have been seeded (make seed-embeddings).
    """
    query_vector = await embed_text(query, settings)

    stmt = (
        select(Rule)
        .where(Rule.embedding.isnot(None))
        .where(Rule.is_active.is_(True))
        .order_by(Rule.embedding.op("<=>")(query_vector))
        .limit(top_k)
    )
    if regulation_id is not None:
        stmt = stmt.where(Rule.regulation_id == regulation_id)

    result = await session.execute(stmt)
    return list(result.scalars().all())
