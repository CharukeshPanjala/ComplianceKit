from pathlib import Path
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
    redis_url: str = "redis://localhost:6379/0"
    environment: str = "development"
    debug: bool = False

    @property
    def is_production(self) -> bool:
        return self.environment == "production"