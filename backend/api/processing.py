from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.db.dependencies import get_db
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
    db: Session = Depends(get_db),
):
    """
    Process a previously uploaded media file.
    """

    service = ProcessingService(db)

    job, video_path, output_directory = service.create_job(
        media_id=request.media_id,
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
def get_job(job_id: str):
    """
    Get the current status of a processing job.
    """

    job = job_manager.get_job(job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found.",
        )

    return job