import os
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session

from backend.db.dependencies import get_db
from backend.models.user import User
from backend.core.dependencies import (
    get_current_user,
    verify_project_ownership,
    verify_media_ownership,
)
from backend.schemas.media import MediaResponse
from backend.services.upload_service import UploadService

router = APIRouter(
    prefix="/projects",
    tags=["Media"],
)


@router.post(
    "/{project_id}/media",
    response_model=MediaResponse,
)
async def upload_media(
    project_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Validate project ownership at the very beginning of the endpoint
    verify_project_ownership(project_id, current_user, db)

    service = UploadService(db)

    return await service.upload(
        project_id=project_id,
        file=file,
    )


@router.get("/media/{media_id}")
def get_media(
    media_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Retrieve media by verifying ownership directly
    media = verify_media_ownership(media_id, current_user, db)

    return {
        "id": media.id,
        "project_id": media.project_id,
        "filename": media.filename,
        "storage_path": media.storage_path,
        "file_size": media.file_size,
        "status": media.status,
        "duration": media.duration,
        "width": media.width,
        "height": media.height,
        "codec": media.codec,
        "bitrate": media.bitrate,
        "fps": media.fps,
    }


@router.get("/media/{media_id}/waveform")
def get_media_waveform(
    media_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Retrieve media by verifying ownership directly
    media = verify_media_ownership(media_id, current_user, db)

    from backend.processing.waveform_processor import WaveformProcessor

    waveform_json_path = Path(media.storage_path).parent / f"{media.id}_waveform.json"
    audio_wav_path = Path(media.storage_path).parent / f"{media.id}_audio.wav"

    peaks = WaveformProcessor.generate_waveform(
        audio_path=audio_wav_path,
        output_json_path=waveform_json_path,
    )

    return {
        "media_id": media.id,
        "peaks": peaks,
    }


@router.delete("/media/{media_id}")
def delete_media(
    media_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Retrieve media by verifying ownership directly
    media = verify_media_ownership(media_id, current_user, db)

    # Clean up files
    try:
        if os.path.exists(media.storage_path):
            os.remove(media.storage_path)
    except Exception:
        pass

    db.delete(media)
    db.commit()

    return {"message": "Media deleted successfully", "media_id": media.id}