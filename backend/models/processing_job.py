from enum import Enum

from pydantic import BaseModel


class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ProcessingJob(BaseModel):
    job_id: str
    filename: str
    status: JobStatus
    user_id: int