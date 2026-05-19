from common.config import BaseServiceSettings

class GatewaySettings(BaseServiceSettings):
    clerk_webhook_secret: str
    cors_origins: list[str] = ["http://localhost:3000"]

settings = GatewaySettings()