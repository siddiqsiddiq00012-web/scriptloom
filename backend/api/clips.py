from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.db.dependencies import get_db
from backend.models.user import User
from backend.core.dependencies import get_current_user, verify_project_ownership, verify_clip_ownership
from backend.repositories.clip_repository import ClipRepository
from backend.storage.manager import storage

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


@router.get("/{clip_id}/stream")
def stream_clip(
    clip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Verify clip ownership before retrieval
    clip = verify_clip_ownership(clip_id, current_user, db)

    if not storage.exists(clip.output_path):
        raise HTTPException(
            status_code=404,
            detail="Clip file not found in storage.",
        )

    filename = clip.title.lower().replace(" ", "_") + ".mp4"
    return StreamingResponse(
        storage.read_stream(clip.output_path),
        media_type="video/mp4",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )