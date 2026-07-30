from pydantic import BaseModel


class VideoMetadata(BaseModel):
    duration: float = 0.0
    width: int | None = None
    height: int | None = None
    codec: str | None = "unknown"
    bitrate: int | None = None
    fps: float | None = None