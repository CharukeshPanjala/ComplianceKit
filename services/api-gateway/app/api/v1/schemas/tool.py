from pydantic import BaseModel


class ToolCreate(BaseModel):
    name: str
    category: str = "other"
    website_url: str | None = None


class ToolResponse(BaseModel):
    tool_id: str
    name: str
    category: str
    website_url: str | None

    model_config = {"from_attributes": True}