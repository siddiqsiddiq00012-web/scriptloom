import logging
from backend.db.database import SessionLocal
from backend.jobs.celery_app import celery_app
from backend.models.media import Media
from backend.models.processing_job import JobStatus, ProcessingJob
from backend.processing.jobs.manager import job_manager
from backend.services.processing_service import ProcessingService
from backend.storage.manager import storage

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_BACKOFF = 30  # seconds
RETRY_BACKOFF_MAX = 300  # seconds


class PermanentFailure(Exception):
    """A failure that retrying will not fix (e.g. missing media record)."""


@celery_app.task(
    name="backend.jobs.tasks.video_processing.process_video",
    bind=True,
    max_retries=MAX_RETRIES,
    default_retry_delay=RETRY_BACKOFF,
    retry_backoff=True,
    retry_backoff_max=RETRY_BACKOFF_MAX,
    retry_jitter=True,
    acks_late=True,
    reject_on_worker_lost=True,
)
def process_video(self, job_id: str):
    db = SessionLocal()
    try:
        # 1. Fetch job record
        job = job_manager.get_job(db, job_id)
        if not job:
            logger.error(f"Job {job_id} not found in database.")
            return

        # 2. Idempotency guard: never re-process a completed job.
        #    Celery redelivers tasks after a worker crash; a job may already
        #    be finished, so skip re-running (avoids double Gemini spend and
        #    duplicate clips).
        if job.status == JobStatus.COMPLETED:
            logger.info(f"Job {job_id} already completed; skipping duplicate execution.")
            return

        # 3. Idempotency guard: if clips already exist for this media,
        #    a previous run finished the pipeline but crashed before the
        #    COMPLETED status was persisted. Promote to COMPLETED instead
        #    of reprocessing.
        media = db.get(Media, job.media_id)
        if media is None:
            logger.error(f"Media {job.media_id} not found for job {job_id}.")
            job_manager.update_status(db, job_id, JobStatus.FAILED, error_message="Media record not found")
            return

        from backend.models.clip import Clip
        clip_count = db.query(Clip).filter(Clip.media_id == media.id).count()
        if clip_count > 0:
            logger.info(f"Job {job_id}: {clip_count} clips already exist for media {media.id}; marking completed without reprocessing.")
            job_manager.update_status(db, job_id, JobStatus.COMPLETED)
            return

        # 4. Check storage object exists before materializing
        if not storage.exists(media.storage_path):
            job_manager.update_status(db, job_id, JobStatus.FAILED, error_message="Source media file not found in storage")
            return

        # 5. Update status to PROCESSING (only after idempotency guards pass)
        job_manager.update_status(db, job_id, JobStatus.PROCESSING)

        # 6. Run the actual processing pipeline service
        processing = ProcessingService(db)
        processing.process_job(
            job_id=job.job_id,
            video_path=media.storage_path,
        )
        db.commit()

    except PermanentFailure as e:
        db.rollback()
        logger.error(f"Permanent failure for job {job_id}: {e}")
        err_db = SessionLocal()
        try:
            job_manager.update_status(err_db, job_id, JobStatus.FAILED, error_message=str(e))
        except Exception as update_err:
            logger.error(f"Failed to write FAILED status for job {job_id}: {update_err}", exc_info=True)
        finally:
            err_db.close()

    except Exception as e:
        db.rollback()
        logger.error(f"Error during video processing job {job_id} (attempt {self.request.retries + 1}): {e}", exc_info=True)

        # Transient errors: retry with exponential backoff + jitter.
        if self.request.retries < MAX_RETRIES:
            try:
                self.retry(exc=e)
            except Exception:
                # Retry budget exhausted — final failure below.
                pass
            finally:
                db.close()
            return

        # Final failure after retries exhausted: mark FAILED.
        err_db = SessionLocal()
        try:
            job_manager.update_status(
                err_db,
                job_id,
                JobStatus.FAILED,
                error_message=f"An unexpected error occurred during processing: {e}",
            )
        except Exception as update_err:
            logger.error(f"Failed to write FAILED status for job {job_id}: {update_err}", exc_info=True)
        finally:
            err_db.close()

        raise e
    finally:
        db.close()
