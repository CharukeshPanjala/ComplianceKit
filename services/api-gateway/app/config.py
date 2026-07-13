from pydantic import Field, field_validator

from common.config import BaseServiceSettings

class GatewaySettings(BaseServiceSettings):
    clerk_webhook_secret: str
    cors_origins: list[str] = Field(default=["http://localhost:3000"])

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list) -> list[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

settings = GatewaySettings()