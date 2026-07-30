from pydantic import BaseModel


class ProcessingRequest(BaseModel):
    media_id: int