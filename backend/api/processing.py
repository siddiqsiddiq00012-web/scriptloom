from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.core.dependencies import get_current_user, verify_media_ownership
from backend.db.dependencies import get_db
from backend.models.user import User
from backend.processing.jobs.manager import job_manager
from backend.schemas.processing import ProcessingRequest
from backend.services.processing_service import ProcessingService

router = APIRouter(
    prefix="/processing",
    tags=["Processing"],
)


@router.post("/process")
def process_video(
    request: ProcessingRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Process a previously uploaded media file.
    """
    # Verify media ownership before starting processing task
    verify_media_ownership(request.media_id, current_user, db)

    service = ProcessingService(db)

    job, video_path, output_directory = service.create_job(
        media_id=request.media_id,
        user_id=current_user.id,
    )

    background_tasks.add_task(
        service.process_job,
        job.job_id,
        video_path,
        output_directory,
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
):
    """
    Get the current status of a processing job.
    """
    job = job_manager.get_job(job_id)

    # Ownership check: Reject unauthorized queries with a sanitized 404
    if job is None or job.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found.",
        )

    return job