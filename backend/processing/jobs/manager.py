import uuid

from backend.models.processing_job import JobStatus, ProcessingJob


class JobManager:
    def __init__(self):
        self.jobs: dict[str, ProcessingJob] = {}

    def create_job(self, filename: str) -> ProcessingJob:
        job = ProcessingJob(
            job_id=str(uuid.uuid4()),
            filename=filename,
            status=JobStatus.PENDING,
        )

        self.jobs[job.job_id] = job
        return job

    def get_job(self, job_id: str):
        return self.jobs.get(job_id)

    def update_status(
        self,
        job_id: str,
        status: JobStatus,
    ):
        if job_id in self.jobs:
            self.jobs[job_id].status = status


job_manager = JobManager()