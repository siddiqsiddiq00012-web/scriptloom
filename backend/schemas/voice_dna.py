from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class VoiceDNAResponse(BaseModel):
    id: int
    user_id: int
    writing_style: str
    tone: str
    vocabulary: str
    cta_style: str
    hook_style: str
    banned_words: str
    emoji_preference: str
    avg_sentence_length: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class VoiceDNAUpdate(BaseModel):
    writing_style: str | None = None
    tone: str | None = None
    vocabulary: str | None = None
    cta_style: str | None = None
    hook_style: str | None = None
    banned_words: str | None = None
    emoji_preference: str | None = None
    avg_sentence_length: int | None = Field(None, ge=5, le=50)
