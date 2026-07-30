from pydantic import BaseModel


class SegmentClip(BaseModel):
    title: str
    start_segment: int
    end_segment: int
    reason: str