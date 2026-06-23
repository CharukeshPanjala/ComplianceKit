import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.engine.embeddings import build_rule_text, search_rules
from common.models.rule import Rule


def make_rule(**kwargs) -> Rule:
    rule = Rule()
    rule.id = uuid.uuid4()
    rule.article = kwargs.get("article", "Article 5")
    rule.title = kwargs.get("title", "Principles of processing")
    rule.description = kwargs.get("description", "Personal data shall be processed lawfully.")
    rule.plain_english = kwargs.get("plain_english", "You must have a legal reason to use data.")
    rule.remediation_hint = kwargs.get("remediation_hint", "Document your legal basis for each activity.")
    rule.is_active = kwargs.get("is_active", True)
    rule.embedding = kwargs.get("embedding", None)
    rule.regulation_id = kwargs.get("regulation_id", uuid.uuid4())
    return rule


# ── build_rule_text ───────────────────────────────────────────────────────────

def test_build_rule_text_includes_article():
    rule = make_rule(article="Article 37", title=None)
    text = build_rule_text(rule)
    assert "Article 37" in text


def test_build_rule_text_includes_title_when_present():
    rule = make_rule(article="Article 5", title="Principles of processing")
    text = build_rule_text(rule)
    assert "Principles of processing" in text


def test_build_rule_text_includes_description():
    rule = make_rule(description="Data shall be collected for specified purposes.")
    text = build_rule_text(rule)
    assert "Data shall be collected for specified purposes." in text


def test_build_rule_text_includes_plain_english():
    rule = make_rule(plain_english="Keep it simple and lawful.")
    text = build_rule_text(rule)
    assert "Plain English: Keep it simple and lawful." in text


def test_build_rule_text_includes_remediation_hint():
    rule = make_rule(remediation_hint="Appoint a DPO.")
    text = build_rule_text(rule)
    assert "Remediation: Appoint a DPO." in text


def test_build_rule_text_skips_none_fields():
    rule = make_rule(title=None, plain_english=None, remediation_hint=None)
    text = build_rule_text(rule)
    assert "Plain English" not in text
    assert "Remediation" not in text
    assert text.strip() != ""


def test_build_rule_text_handles_missing_article():
    rule = make_rule(article=None)
    text = build_rule_text(rule)
    assert rule.description in text


# ── search_rules ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_search_rules_embeds_query_and_returns_results():
    fake_vector = [0.1] * 1536
    fake_rule = make_rule(embedding=fake_vector)

    mock_settings = MagicMock()
    mock_settings.azure_openai_deployment_embeddings = "text-embedding-3-small"

    mock_client = AsyncMock()
    mock_client.embeddings.create.return_value = MagicMock(
        data=[MagicMock(embedding=fake_vector)]
    )

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [fake_rule]
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars

    mock_session = AsyncMock()
    mock_session.execute = AsyncMock(return_value=mock_result)

    with patch("app.engine.embeddings.get_async_client", return_value=mock_client):
        results = await search_rules(
            query="What is the legal basis for processing?",
            session=mock_session,
            settings=mock_settings,
            top_k=5,
        )

    assert len(results) == 1
    assert results[0].article == fake_rule.article
    mock_client.embeddings.create.assert_called_once_with(
        model="text-embedding-3-small",
        input="What is the legal basis for processing?",
    )


@pytest.mark.asyncio
async def test_search_rules_filters_by_regulation_id():
    fake_vector = [0.0] * 1536
    reg_id = uuid.uuid4()

    mock_settings = MagicMock()
    mock_settings.azure_openai_deployment_embeddings = "text-embedding-3-small"

    mock_client = AsyncMock()
    mock_client.embeddings.create.return_value = MagicMock(
        data=[MagicMock(embedding=fake_vector)]
    )

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = []
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars

    mock_session = AsyncMock()
    mock_session.execute = AsyncMock(return_value=mock_result)

    with patch("app.engine.embeddings.get_async_client", return_value=mock_client):
        results = await search_rules(
            query="security measures",
            session=mock_session,
            settings=mock_settings,
            top_k=3,
            regulation_id=reg_id,
        )

    assert results == []
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_search_rules_returns_empty_when_no_embeddings():
    fake_vector = [0.0] * 1536

    mock_settings = MagicMock()
    mock_settings.azure_openai_deployment_embeddings = "text-embedding-3-small"

    mock_client = AsyncMock()
    mock_client.embeddings.create.return_value = MagicMock(
        data=[MagicMock(embedding=fake_vector)]
    )

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = []
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars

    mock_session = AsyncMock()
    mock_session.execute = AsyncMock(return_value=mock_result)

    with patch("app.engine.embeddings.get_async_client", return_value=mock_client):
        results = await search_rules(
            query="breach notification",
            session=mock_session,
            settings=mock_settings,
        )

    assert results == []
