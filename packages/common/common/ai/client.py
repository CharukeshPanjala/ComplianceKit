from __future__ import annotations

from typing import TYPE_CHECKING

from openai import AsyncAzureOpenAI, AzureOpenAI

if TYPE_CHECKING:
    from common.config import AIServiceSettings


def get_async_client(settings: AIServiceSettings) -> AsyncAzureOpenAI:
    """
    Async Azure OpenAI client — use in FastAPI endpoints and background tasks.

    Usage:
        client = get_async_client(settings)
        response = await client.chat.completions.create(
            model=settings.azure_openai_deployment_gpt4o,
            messages=[...],
        )
    """
    return AsyncAzureOpenAI(
        azure_endpoint=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_api_key,
        api_version=settings.azure_openai_api_version,
    )


def get_sync_client(settings: AIServiceSettings) -> AzureOpenAI:
    """
    Sync Azure OpenAI client — use in CLI scripts and seeders (COM-158/159/160/187).

    Usage:
        client = get_sync_client(settings)
        response = client.embeddings.create(
            model=settings.azure_openai_deployment_embeddings,
            input="Article text here",
        )
    """
    return AzureOpenAI(
        azure_endpoint=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_api_key,
        api_version=settings.azure_openai_api_version,
    )