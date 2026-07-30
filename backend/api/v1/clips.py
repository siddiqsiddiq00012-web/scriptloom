from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.auth.security import get_current_user
from backend.db.database import get_db
from backend.models.user import User
from backend.schemas.clip import (
    ClipCreate,
    ClipResponse,
    ClipUpdate,
)
from backend.services.clip_service import ClipService

router = APIRouter(
    prefix="/clips",
    tags=["Clips"],
)


@router.post(
    "/projects/{project_id}",
    response_model=ClipResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_clip(
    project_id: int,
    clip: ClipCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ClipService(db)

    try:
        return service.create_clip(project_id, clip)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.get(
    "/projects/{project_id}",
    response_model=list[ClipResponse],
)
def list_project_clips(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ClipService(db)
    return service.list_project_clips(project_id)


@router.get(
    "/{clip_id}",
    response_model=ClipResponse,
)
def get_clip(
    clip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ClipService(db)

    clip = service.get_clip(clip_id)

    if clip is None:
        raise HTTPException(
            status_code=404,
            detail="Clip not found",
        )

    return clip


@router.patch(
    "/{clip_id}",
    response_model=ClipResponse,
)
def update_clip(
    clip_id: int,
    clip_update: ClipUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ClipService(db)

    try:
        return service.update_clip(
            clip_id,
            clip_update,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.delete("/{clip_id}")
def delete_clip(
    clip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ClipService(db)

    try:
        service.delete_clip(clip_id)
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    return {
        "message": "Clip deleted successfully"
    }