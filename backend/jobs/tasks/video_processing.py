from backend.db.database import SessionLocal
from backend.jobs.celery_app import celery_app
from backend.models.media import Media
from backend.services.processing_service import ProcessingService


@celery_app.task
def process_video(media_id: int):
    db = SessionLocal()

    try:
        media = db.get(Media, media_id)

        if media is None:
            return

        media.status = "processing"
        db.commit()

        processing = ProcessingService(db)

        job, video_path, output_directory = processing.create_job(
            media_id
        )

        processing.process_job(
            job.job_id,
            video_path,
            output_directory,
        )

        media.status = "completed"
        db.commit()

    except Exception:
        db.rollback()

        media = db.get(Media, media_id)

        if media is not None:
            media.status = "failed"
            db.commit()

        raise

    finally:
        db.close()