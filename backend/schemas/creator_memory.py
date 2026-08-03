from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class MemorySearchRequest(BaseModel):
    query: str = Field(..., min_length=2)
    category: str | None = None  # quote | story | framework | analogy | customer_insight | None
    top_k: int = Field(5, ge=1, le=20)


class MemoryItemResponse(BaseModel):
    id: int
    user_id: int
    media_id: int | None = None
    category: str
    quote_text: str
    context: str | None = None
    score: float | None = 1.0
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class MemoryIndexResponse(BaseModel):
    message: str
    indexed_count: int
    media_id: int
