import time
import uuid
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel, Field


class ProgressState(str, Enum):
    QUEUED = "queued"
    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    AUDIO_EXTRACTED = "audio_extracted"
    TRANSCRIBING = "transcribing"
    TRANSCRIPT_COMPLETED = "transcript_completed"
    EMBEDDING = "embedding"
    VOICE_DNA = "voice_dna"
    CAMPAIGN_GENERATING = "campaign_generating"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class EventSchema(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str  # e.g., 'media.processing.started'
    timestamp: float = Field(default_factory=time.time)
    user_id: Optional[int] = None
    project_id: Optional[int] = None
    media_id: Optional[int] = None
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    version: str = "1.0"
    payload: Dict[str, Any] = Field(default_factory=dict)


class EventBus:
    def __init__(self):
        # event_type -> list of listener callbacks
        self._subscribers: Dict[str, List[Callable[[EventSchema], None]]] = {}

    def subscribe(self, event_type: str, callback: Callable[[EventSchema], None]):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def publish(self, event: EventSchema):
        # Notify specific event subscribers
        if event.event_type in self._subscribers:
            for cb in self._subscribers[event.event_type]:
                try:
                    cb(event)
                except Exception as exc:
                    print(f"Error executing event subscriber callback for {event.event_type}: {exc}")

        # Notify wildcard '*' subscribers
        if "*" in self._subscribers:
            for cb in self._subscribers["*"]:
                try:
                    cb(event)
                except Exception as exc:
                    print(f"Error executing wildcard event subscriber callback: {exc}")


# Global Event Bus Instance
event_bus = EventBus()
