from common.config import AIServiceSettings

class PolicySettings(AIServiceSettings):
    internal_api_key: str = ""
    cors_origins: list[str] = ["http://localhost:3000"]

settings = PolicySettings()