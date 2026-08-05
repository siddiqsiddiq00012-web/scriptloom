import logging
from backend.db.database import SessionLocal
from backend.jobs.celery_app import celery_app
from backend.models.media import Media
from backend.models.processing_job import JobStatus, ProcessingJob
from backend.processing.jobs.manager import job_manager
from backend.services.processing_service import ProcessingService
from backend.storage.manager import storage

logger = logging.getLogger(__name__)

@celery_app.task(name="backend.jobs.tasks.video_processing.process_video")
def process_video(job_id: str):
    db = SessionLocal()
    try:
        # 1. Fetch job record
        job = job_manager.get_job(db, job_id)
        if not job:
            logger.error(f"Job {job_id} not found in database.")
            return

        # 2. Update status to PROCESSING
        job_manager.update_status(db, job_id, JobStatus.PROCESSING)

        # 3. Fetch media record
        media = db.get(Media, job.media_id)
        if media is None:
            job_manager.update_status(db, job_id, JobStatus.FAILED, error_message="Media record not found")
            return

        # 4. Check storage object exists before materializing
        if not storage.exists(media.storage_path):
            job_manager.update_status(db, job_id, JobStatus.FAILED, error_message="Source media file not found in storage")
            return

        # 5. Run the actual processing pipeline service
        processing = ProcessingService(db)
        processing.process_job(
            job_id=job.job_id,
            video_path=media.storage_path,
        )
        db.commit()

    except Exception as e:
        db.rollback()
        logger.error(f"Error during video processing job {job_id}: {e}", exc_info=True)
        
        # Use a separate, fresh session to write failure status to DB
        err_db = SessionLocal()
        try:
            job_manager.update_status(
                err_db,
                job_id,
                JobStatus.FAILED,
                error_message="An unexpected error occurred during processing."
            )
        except Exception as update_err:
            logger.error(f"Failed to write FAILED status for job {job_id}: {update_err}", exc_info=True)
        finally:
            err_db.close()
            
        raise e
    finally:
        db.close()