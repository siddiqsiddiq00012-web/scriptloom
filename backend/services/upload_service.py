import uuid
import os
import logging
import tempfile
from pathlib import Path
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

logger = logging.getLogger("scriptloom.uploads")

from backend.repositories.media_repository import MediaRepository
from backend.repositories.project_repository import ProjectRepository
from backend.services.ffprobe_service import FFprobeService
from backend.services.file_sanitizer import FileSanitizer
from backend.storage.manager import storage

ALLOWED_EXTENSIONS = {
    ".mp4",
    ".mov",
    ".avi",
    ".mkv",
    ".webm",
    ".mp3",
    ".wav",
    ".m4a",
    ".aac",
    ".flac",
}

MAX_FILE_SIZE = 4 * 1024 * 1024 * 1024  # 4 GB


class UploadService:

    def __init__(self, db: Session):
        self.db = db
        self.projects = ProjectRepository(db)
        self.media = MediaRepository(db)

    async def upload(
        self,
        *,
        project_id: int,
        file: UploadFile,
    ):
        project = self.projects.get_by_id(project_id)

        if project is None:
            raise HTTPException(
                status_code=404,
                detail="Project not found.",
            )

        raw_filename = file.filename or "upload"
        clean_original_name = FileSanitizer.sanitize_filename(raw_filename)
        extension = Path(clean_original_name).suffix.lower()

        if extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type '{extension}'. Supported: {', '.join(ALLOWED_EXTENSIONS)}",
            )

        temp_dir = Path(tempfile.mkdtemp(prefix="upload_temp_"))
        temp_path = temp_dir / f"upload_{uuid.uuid4()}{extension}"

        try:
            # 1. Copy streaming upload to local temp file to avoid buffering in RAM
            file.file.seek(0)
            file_size = 0
            with open(temp_path, "wb") as f:
                while True:
                    chunk = file.file.read(8 * 1024 * 1024)  # 8MB chunking
                    if not chunk:
                        break
                    file_size += len(chunk)
                    if file_size > MAX_FILE_SIZE:
                        raise HTTPException(
                            status_code=400,
                            detail="File exceeds maximum size limit of 4GB",
                        )
                    f.write(chunk)

            # 2. Layered validation
            # - Magic-byte header check (defense in depth before ffprobe)
            with open(temp_path, "rb") as fh:
                header_bytes = fh.read(32)
            FileSanitizer.validate_magic_bytes(header_bytes)

            # - Advisory MIME verification
            declared_mime = file.content_type
            
            # - Authoritative FFprobe format validation
            try:
                metadata = FFprobeService.extract_metadata(temp_path)
            except Exception as e:
                logger.warning("Upload rejected: ffprobe validation failed for %s: %s", temp_path, e)
                raise HTTPException(
                    status_code=400,
                    detail="Invalid media file. The file could not be read as a valid video or audio file.",
                )

            # 3. Stream to persistent storage with canonical key
            storage_key = f"projects/{project_id}/media/{uuid.uuid4()}{extension}"
            
            def _chunk_iterator():
                with open(temp_path, "rb") as f:
                    while True:
                        chunk = f.read(8 * 1024 * 1024)
                        if not chunk:
                            break
                        yield chunk

            try:
                storage.save_stream(storage_key, _chunk_iterator(), file_size)
            except Exception as e:
                logger.error("Storage upload failed for key %s: %s", storage_key, e)
                raise HTTPException(
                    status_code=500,
                    detail="Storage upload failed. Please try again.",
                )

            # 4. Create database record with transactional cleanup rollback
            try:
                media = self.media.create_media(
                    project_id=project.id,
                    filename=clean_original_name,
                    storage_path=storage_key,
                    file_size=file_size,
                    metadata=metadata,
                )
            except Exception as db_err:
                # Compensation rollback: delete persistent object on DB failure
                try:
                    storage.delete(storage_key)
                except Exception:
                    pass
                raise db_err

            # Run Media Processing Pipeline (Audio Extraction & Waveform Generation)
            from backend.services.media_pipeline import MediaPipeline
            processed_media = MediaPipeline(self.db).process_media(media.id)

            return processed_media if processed_media else media

        finally:
            # Cleanup temp file and dir
            if temp_path.exists():
                try:
                    os.remove(temp_path)
                except Exception:
                    pass
            if temp_dir.exists():
                try:
                    os.rmdir(temp_dir)
                except Exception:
                    pass