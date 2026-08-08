import asyncio
import json
import time
from typing import Dict, List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.db.dependencies import get_db
from backend.core.dependencies import get_current_user, verify_media_ownership
from backend.models.user import User
from backend.events.event_bus import event_bus, EventSchema

router = APIRouter(
    prefix="/stream",
    tags=["SSE Progress Stream"],
)


class SSEHub:
    def __init__(self):
        # media_id -> list of asyncio queues
        self.subscribers: Dict[int, List[asyncio.Queue]] = {}

        # Connect EventBus to SSE Hub fan-out
        event_bus.subscribe("*", self.on_event_published)

    def on_event_published(self, event: EventSchema):
        if event.media_id and event.media_id in self.subscribers:
            data_str = event.model_dump_json()
            for q in self.subscribers[event.media_id]:
                try:
                    q.put_nowait(data_str)
                except Exception:
                    pass

    def add_client(self, media_id: int) -> asyncio.Queue:
        if media_id not in self.subscribers:
            self.subscribers[media_id] = []
        q = asyncio.Queue()
        self.subscribers[media_id].append(q)
        return q

    def remove_client(self, media_id: int, q: asyncio.Queue):
        if media_id in self.subscribers and q in self.subscribers[media_id]:
            self.subscribers[media_id].remove(q)
            if not self.subscribers[media_id]:
                del self.subscribers[media_id]


sse_hub = SSEHub()


@router.get("/progress/{media_id}")
async def stream_media_progress(
    media_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Verify media ownership before subscribing to progress event stream
    verify_media_ownership(media_id, current_user, db)

    q = sse_hub.add_client(media_id)

    async def _event_generator():
        try:
            # Emit initial connection state
            init_event = {
                "event": "connected",
                "media_id": media_id,
                "timestamp": time.time(),
            }
            yield f"data: {json.dumps(init_event)}\n\n"

            while True:
                try:
                    # Wait for next event with 15s keepalive timeout
                    data = await asyncio.wait_for(q.get(), timeout=15.0)
                    yield f"data: {data}\n\n"
                except asyncio.TimeoutError:
                    # Emit structured heartbeat frame
                    heartbeat = {
                        "event": "heartbeat",
                        "timestamp": time.time(),
                        "server_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    }
                    yield f"data: {json.dumps(heartbeat)}\n\n"
        finally:
            sse_hub.remove_client(media_id, q)

    return StreamingResponse(
        _event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
