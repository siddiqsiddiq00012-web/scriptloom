from pydantic import BaseModel


class ProcessUploadRequest(BaseModel):
    filename: str