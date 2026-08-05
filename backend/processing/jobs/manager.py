import uuid
from sqlalchemy.orm import Session
from backend.models.processing_job import JobStatus, ProcessingJob

class JobManager:
    def create_job(self, db: Session, media_id: int, user_id: int) -> ProcessingJob:
        # Obtain media filename
        from backend.models.media import Media
        media = db.get(Media, media_id)
        filename = media.filename if media else "unknown"

        job = ProcessingJob(
            job_id=str(uuid.uuid4()),
            media_id=media_id,
            filename=filename,
            status=JobStatus.PENDING,
            user_id=user_id,
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job

    def get_job(self, db: Session, job_id: str) -> ProcessingJob | None:
        return db.query(ProcessingJob).filter(ProcessingJob.job_id == job_id).first()

    def update_status(
        self,
        db: Session,
        job_id: str,
        status: JobStatus,
        error_message: str | None = None,
    ) -> None:
        job = self.get_job(db, job_id)
        if job:
            job.status = status
            if error_message is not None:
                job.error_message = error_message
            db.commit()

job_manager = JobManager()