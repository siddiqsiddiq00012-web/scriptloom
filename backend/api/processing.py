import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError

from backend.core.dependencies import get_current_user, verify_media_ownership
from backend.db.dependencies import get_db
from backend.models.user import User
from backend.models.media import Media
from backend.models.project import Project
from backend.models.processing_job import JobStatus, ProcessingJob
from backend.processing.jobs.manager import job_manager
from backend.schemas.processing import ProcessingRequest
from backend.jobs.tasks.video_processing import process_video as process_video_task
from backend.services.billing_service import BillingService
from backend.services.feature_gate import Feature

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/processing",
    tags=["Processing"],
)


@router.post("/process")
def process_video(
    request: ProcessingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Process a previously uploaded media file.
    """
    # 1. Verify media ownership before starting processing task
    verify_media_ownership(request.media_id, current_user, db)

    # 2. Check usage limits before starting processing
    billing_service = BillingService(db)
    media = db.get(Media, request.media_id)
    processing_seconds = int(media.duration or 0) if media else 0
    billing_service.check_quota(
        current_user,
        Feature.PROCESSING,
        additional=max(1, processing_seconds // 60),
    )

    # 3. Persist job entry in the database with concurrency safety
    try:
        job = job_manager.create_job(
            db=db,
            media_id=request.media_id,
            user_id=current_user.id,
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An active processing job is already running for this media."
        )

    # 3. Offload execution out-of-process via Celery
    try:
        process_video_task.delay(job.job_id)
    except Exception as e:
        logger.error(f"Celery task dispatch failed for job {job.job_id}: {e}", exc_info=True)
        # Compensation: Update job status to FAILED
        job_manager.update_status(
            db=db,
            job_id=job.job_id,
            status=JobStatus.FAILED,
            error_message="Task queue dispatch failed"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to queue the media processing task. Please try again."
        )

    return {
        "success": True,
        "job_id": job.job_id,
        "status": job.status,
    }


@router.get("/jobs/{job_id}")
def get_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get the current status of a processing job.
    """
    # 1. Query the job database entry
    job = job_manager.get_job(db, job_id)

    # 2. Ownership check: Query Media and Project to establish ownership path
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found.",
        )

    media = db.get(Media, job.media_id)
    if media is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found.",
        )

    project = db.get(Project, media.project_id)
    if project is None or project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found.",
        )

    return {
        "job_id": job.job_id,
        "media_id": job.media_id,
        "user_id": job.user_id,
        "status": job.status,
        "error_message": job.error_message,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
    }

@router.get("/jobs")
def list_user_jobs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all processing jobs for the current user."""
    jobs = (
        db.query(ProcessingJob)
        .filter(ProcessingJob.user_id == current_user.id)
        .order_by(desc(ProcessingJob.created_at))
        .limit(50)
        .all()
    )
    return [
        {
            "job_id": job.job_id,
            "media_id": job.media_id,
            "user_id": job.user_id,
            "filename": job.filename,
            "status": job.status,
            "error_message": job.error_message,
            "created_at": job.created_at,
            "updated_at": job.updated_at,
        }
        for job in jobs
    ]

@router.get("/media/{media_id}/jobs/latest")
def get_latest_job_for_media(
    media_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get the most recent processing job for a specific media resource.
    """
    # 1. Verify media ownership
    verify_media_ownership(media_id, current_user, db)

    # 2. Query the latest job for this media
    job = (
        db.query(ProcessingJob)
        .filter(ProcessingJob.media_id == media_id)
        .order_by(desc(ProcessingJob.created_at))
        .first()
    )

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No processing jobs found for this media.",
        )

    return {
        "job_id": job.job_id,
        "media_id": job.media_id,
        "user_id": job.user_id,
        "status": job.status,
        "error_message": job.error_message,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
    }
