from common.config import BaseServiceSettings

class GatewaySettings(BaseServiceSettings):
    clerk_webhook_secret: str

settings = GatewaySettings()