import os
import json
import tempfile
import shutil
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.db.dependencies import get_db
from backend.models.user import User
from backend.core.dependencies import (
    get_current_user,
    verify_project_ownership,
    verify_media_ownership,
)
from backend.schemas.media import MediaResponse
from backend.services.upload_service import UploadService
from backend.storage.manager import storage
from backend.storage.base import validate_storage_key

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


@router.get("/{project_id}/media")
def list_project_media(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all media items belonging to a project (ownership verified)."""
    verify_project_ownership(project_id, current_user, db)

    from backend.models.media import Media
    media_items = (
        db.query(Media)
        .filter(Media.project_id == project_id)
        .order_by(desc(Media.id))
        .all()
    )

    return [
        {
            "id": m.id,
            "project_id": m.project_id,
            "filename": m.filename,
            "storage_path": m.storage_path,
            "file_size": m.file_size,
            "status": m.status,
            "duration": m.duration,
            "width": m.width,
            "height": m.height,
            "codec": m.codec,
            "bitrate": m.bitrate,
            "fps": m.fps,
        }
        for m in media_items
    ]


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

    waveform_key = f"projects/{media.project_id}/waveforms/{media.id}_waveform.json"

    # Check if waveform JSON exists in storage
    if storage.exists(waveform_key):
        try:
            # Stream download to avoid loading large objects fully in RAM
            chunks = list(storage.read_stream(waveform_key))
            peaks = json.loads(b"".join(chunks).decode("utf-8"))
            return {
                "media_id": media.id,
                "peaks": peaks,
            }
        except Exception as e:
            # Handle corrupted or unreadable objects, fallback to recomputation
            print(f"[Waveform Storage Error] Failed to read {waveform_key}: {e}")

    # Recompute peaks inside temp workspace if not found in persistent storage
    from backend.processing.waveform_processor import WaveformProcessor
    from backend.processing.audio_processor import AudioProcessor

    with storage.materialize(media.storage_path) as local_media_path:
        temp_dir = Path(tempfile.mkdtemp(prefix="waveform_recompute_"))
        temp_audio_path = temp_dir / f"{media.id}_audio.wav"
        temp_waveform_path = temp_dir / f"{media.id}_waveform.json"

        try:
            AudioProcessor.extract_audio(local_media_path, temp_audio_path)
            peaks = WaveformProcessor.generate_waveform(temp_audio_path, temp_waveform_path)

            # Persist back to storage
            file_size = temp_waveform_path.stat().st_size
            with open(temp_waveform_path, "rb") as wf:
                def _wf_gen():
                    while True:
                        chunk = wf.read(1024 * 1024)
                        if not chunk:
                            break
                        yield chunk
                storage.save_stream(waveform_key, _wf_gen(), file_size)

            return {
                "media_id": media.id,
                "peaks": peaks,
            }
        finally:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)


@router.delete("/media/{media_id}")
def delete_media(
    media_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 1. Authenticate and verify ownership directly
    media = verify_media_ownership(media_id, current_user, db)

    # 2. Collect every persistent storage key before changing database state
    keys_to_delete = []
    if media.storage_path:
        keys_to_delete.append(media.storage_path)

    waveform_key = f"projects/{media.project_id}/waveforms/{media.id}_waveform.json"
    keys_to_delete.append(waveform_key)

    from backend.models.clip import Clip
    clips = db.query(Clip).filter(Clip.media_id == media.id).all()
    for clip in clips:
        if clip.output_path:
            keys_to_delete.append(clip.output_path)
        if clip.subtitle_path:
            keys_to_delete.append(clip.subtitle_path)

    # Validate keys
    for key in keys_to_delete:
        try:
            validate_storage_key(key)
        except Exception as err:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid storage key: {str(err)}",
            )

    # 3. Attempt deletion of associated storage objects
    for key in keys_to_delete:
        try:
            if storage.exists(key):
                storage.delete(key)
        except Exception as e:
            # 4. Log detailed server-side error, return sanitized response, and abort DB delete
            print(f"[STORAGE DELETION ERROR] Failed to delete key {key}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to delete associated storage objects. Deletion aborted.",
            )

    # 5. DB deletion occurs only after storage cleanup succeeds
    try:
        db.delete(media)
        db.commit()
    except Exception as db_err:
        # 6. Rollback DB and log inconsistency
        db.rollback()
        print(f"[DATABASE INCONSISTENCY ERROR] DB delete failed after storage objects were deleted: {str(db_err)}")
        raise HTTPException(
            status_code=500,
            detail="Database record deletion failed. Storage state may be inconsistent.",
        )

    return {"message": "Media deleted successfully", "media_id": media_id}


@router.get("/media/{media_id}/stream")
def stream_media(
    media_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Verify media ownership before retrieval
    media = verify_media_ownership(media_id, current_user, db)

    if not storage.exists(media.storage_path):
        raise HTTPException(
            status_code=404,
            detail="Media file not found in storage.",
        )

    raw_filename = media.filename
    media_type = "video/mp4" if raw_filename.lower().endswith((".mp4", ".mov", ".avi", ".mkv", ".webm")) else "audio/mpeg"
    
    # Use safe ASCII filename for Content-Disposition to avoid latin-1 encoding errors
    safe_filename = raw_filename.encode("ascii", errors="ignore").decode("ascii").strip()
    if not safe_filename:
        ext = Path(raw_filename).suffix or ".mp4"
        safe_filename = f"media_{media.id}{ext}"

    return StreamingResponse(
        storage.read_stream(media.storage_path),
        media_type=media_type,
        headers={"Content-Disposition": f'inline; filename="{safe_filename}"'},
    )