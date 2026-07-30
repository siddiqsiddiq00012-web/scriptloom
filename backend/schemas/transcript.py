from datetime import datetime
from pydantic import BaseModel, ConfigDict


class TranscriptSegmentResponse(BaseModel):
    id: int
    transcript_id: int
    speaker_label: str
    start_time: float
    end_time: float
    text: str
    chapter_title: str | None = None
    key_assertion: str | None = None

    model_config = ConfigDict(from_attributes=True)


class TranscriptResponse(BaseModel):
    id: int
    media_id: int
    language: str
    full_text: str
    summary: str | None = None
    status: str
    created_at: datetime | None = None
    segments: list[TranscriptSegmentResponse] = []

    model_config = ConfigDict(from_attributes=True)


class SegmentUpdate(BaseModel):
    speaker_label: str | None = None
    text: str | None = None
    chapter_title: str | None = None
