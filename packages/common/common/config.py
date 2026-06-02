from pathlib import Path
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[3]

class BaseServiceSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ROOT_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    database_url: str
    app_user_database_url: str = ""
    redis_url: str = "redis://localhost:6379/0"
    environment: str = "development"
    debug: bool = False

    @field_validator("database_url", mode="before")
    @classmethod
    def fix_database_url(cls, v: str) -> str:
        if v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    @field_validator("app_user_database_url", mode="before")
    @classmethod
    def fix_app_user_database_url(cls, v: str) -> str:
        if v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


class AIServiceSettings(BaseServiceSettings):
    """Extended settings for services that use Azure OpenAI."""

    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_api_version: str = "2024-10-21"
    azure_openai_deployment_gpt4o: str = "gpt-4o"
    azure_openai_deployment_embeddings: str = "text-embedding-3-small"

    @property
    def ai_enabled(self) -> bool:
        return bool(self.azure_openai_endpoint and self.azure_openai_api_key)