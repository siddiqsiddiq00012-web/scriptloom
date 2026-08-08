from datetime import datetime
from pydantic import BaseModel, ConfigDict


class GeneratedContentResponse(BaseModel):
    id: int
    media_id: int
    project_id: int
    content_type: str
    title: str
    body_json: str
    status: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class CampaignPackResponse(BaseModel):
    media_id: int
    project_id: int
    count: int
    assets: list[GeneratedContentResponse] = []


class ContentUpdate(BaseModel):
    title: str | None = None
    body_json: str | None = None


class ContentGenerationRequest(BaseModel):
    content_type: str
    tone: str | None = None
    audience: str | None = None
    length: str | None = None
    extra_instructions: str | None = None


class ContentTypeOption(BaseModel):
    key: str
    label: str
    description: str
    category: str
    available: bool = True
