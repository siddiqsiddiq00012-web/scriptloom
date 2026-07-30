import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from backend.jobs.tasks.video_processing import process_video
from backend.repositories.media_repository import MediaRepository
from backend.repositories.project_repository import ProjectRepository
from backend.services.ffprobe_service import FFprobeService
from backend.services.processing_service import ProcessingService
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
                detail="Project not found",
            )

        extension = Path(file.filename).suffix.lower()

        if extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type '{extension}'. Supported: {', '.join(ALLOWED_EXTENSIONS)}",
            )

        content = await file.read()

        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail="File exceeds maximum size limit of 4GB",
            )

        filename = f"{uuid.uuid4()}{extension}"

        path = await storage.save(
            filename,
            content,
        )

        metadata = FFprobeService.extract_metadata(path)

        media = self.media.create_media(
            project_id=project.id,
            filename=filename,
            storage_path=path,
            file_size=len(content),
            metadata=metadata,
        )

        # Run Media Processing Pipeline (Audio Extraction & Waveform Generation)
        from backend.services.media_pipeline import MediaPipeline
        processed_media = MediaPipeline(self.db).process_media(media.id)

        return processed_media if processed_media else media