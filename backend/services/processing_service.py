import traceback
from pathlib import Path

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.models.processing_job import JobStatus, ProcessingJob
from backend.processing.jobs.manager import job_manager
from backend.processing.pipeline.service import ProcessingPipeline
from backend.repositories.clip_repository import ClipRepository
from backend.repositories.media_repository import MediaRepository


class ProcessingService:
    """
    Handles the business logic for processing uploaded media.
    """

    def __init__(self, db: Session):
        self.media_repository = MediaRepository(db)
        self.clip_repository = ClipRepository(db)

    def create_job(
        self,
        media_id: int,
    ) -> tuple[ProcessingJob, str, str]:

        media = self.media_repository.get_by_id(media_id)

        if media is None:
            raise HTTPException(
                status_code=404,
                detail="Media not found.",
            )

        video_path = Path(media.storage_path)

        if not video_path.exists():
            raise HTTPException(
                status_code=404,
                detail="Uploaded media file not found.",
            )

        output_directory = Path("media/output") / video_path.stem

        output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        job = job_manager.create_job(media.filename)

        return (
            job,
            str(video_path),
            str(output_directory),
        )

    def process_job(
        self,
        job_id: str,
        video_path: str,
        output_directory: str,
    ) -> None:
        """
        Execute the processing pipeline.
        """

        try:
            job_manager.update_status(
                job_id,
                JobStatus.PROCESSING,
            )

            media = self.media_repository.get_by_path(video_path)

            if media is None:
                raise RuntimeError(
                    "Media record not found."
                )

            pipeline = ProcessingPipeline()

            generated_clips = pipeline.process_video(
                video_path=video_path,
                output_directory=output_directory,
            )

            subtitle_path = str(
                Path(output_directory) / "subtitles.srt"
            )

            for clip in generated_clips:
                self.clip_repository.create(
                    project_id=media.project_id,
                    media_id=media.id,
                    title=clip["title"],
                    start_time=clip["start_time"],
                    end_time=clip["end_time"],
                    reason=clip["reason"],
                    output_path=clip["output"],
                    subtitle_path=subtitle_path,
                )

            job_manager.update_status(
                job_id,
                JobStatus.COMPLETED,
            )

        except Exception:
            traceback.print_exc()

            job_manager.update_status(
                job_id,
                JobStatus.FAILED,
            )