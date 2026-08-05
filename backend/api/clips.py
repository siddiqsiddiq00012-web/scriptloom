from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.db.dependencies import get_db
from backend.models.user import User
from backend.core.dependencies import get_current_user, verify_project_ownership
from backend.repositories.clip_repository import ClipRepository

router = APIRouter(
    prefix="/clips",
    tags=["Clips"],
)


@router.get("/project/{project_id}")
def get_project_clips(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Verify project ownership before listing clips
    verify_project_ownership(project_id, current_user, db)

    repository = ClipRepository(db)
    clips = repository.get_project_clips(project_id)

    return [
        {
            "id": clip.id,
            "project_id": clip.project_id,
            "media_id": clip.media_id,
            "title": clip.title,
            "start_time": clip.start_time,
            "end_time": clip.end_time,
            "reason": clip.reason,
            "output_path": clip.output_path,
            "subtitle_path": clip.subtitle_path,
        }
        for clip in clips
    ]