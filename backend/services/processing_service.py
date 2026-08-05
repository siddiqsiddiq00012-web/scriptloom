import traceback
import uuid
import tempfile
import os
import shutil
from pathlib import Path
from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.models.processing_job import JobStatus, ProcessingJob
from backend.processing.jobs.manager import job_manager
from backend.processing.pipeline.service import ProcessingPipeline
from backend.repositories.clip_repository import ClipRepository
from backend.repositories.media_repository import MediaRepository
from backend.storage.manager import storage


class ProcessingService:
    """
    Handles the business logic for processing uploaded media.
    """

    def __init__(self, db: Session):
        self.db = db
        self.media_repository = MediaRepository(db)
        self.clip_repository = ClipRepository(db)

    def create_job(
        self,
        media_id: int,
        user_id: int,
    ) -> tuple[ProcessingJob, str, str]:
        media = self.media_repository.get_by_id(media_id)

        if media is None:
            raise HTTPException(
                status_code=404,
                detail="Media not found.",
            )

        # R2-aware check: use exists() on the storage path key
        if not storage.exists(media.storage_path):
            raise HTTPException(
                status_code=404,
                detail="Uploaded media file not found in storage.",
            )

        job = job_manager.create_job(media.filename, user_id)

        # In R2 architecture, these two string params are dummy identifiers
        # because the process_job background task dynamically materializes paths.
        return (
            job,
            media.storage_path,
            f"dummy_output_{media.id}",
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
        uploaded_keys = []

        try:
            job_manager.update_status(
                job_id,
                JobStatus.PROCESSING,
            )

            # video_path here is the media.storage_path key
            media = self.media_repository.get_by_path(video_path)

            if media is None:
                raise RuntimeError("Media record not found.")

            # A. Materialize the remote/local file context
            with storage.materialize(media.storage_path) as materialized_video_path:
                # B. Create temporary directory for FFmpeg workspace
                with tempfile.TemporaryDirectory(prefix="process_job_") as temp_dir_str:
                    temp_output_dir = Path(temp_dir_str)

                    pipeline = ProcessingPipeline()
                    generated_clips = pipeline.process_video(
                        video_path=str(materialized_video_path),
                        output_directory=str(temp_output_dir),
                    )

                    # 1. Upload subtitles to storage if they were generated
                    temp_subtitle_path = temp_output_dir / "subtitles.srt"
                    subtitle_key = ""
                    if temp_subtitle_path.exists():
                        subtitle_key = f"projects/{media.project_id}/subtitles/{media.id}_subtitles.srt"
                        file_size = temp_subtitle_path.stat().st_size
                        with open(temp_subtitle_path, "rb") as sf:
                            def _sf_gen():
                                while True:
                                    chunk = sf.read(1024 * 1024)
                                    if not chunk:
                                        break
                                    yield chunk
                            storage.save_stream(subtitle_key, _sf_gen(), file_size)
                            uploaded_keys.append(subtitle_key)

                    # 2. Upload clips to storage dynamically
                    final_clips_to_create = []
                    for idx, clip in enumerate(generated_clips, start=1):
                        clip_file = Path(clip["output"])
                        if not clip_file.exists():
                            raise FileNotFoundError(f"Extracted clip file not found: {clip_file}")

                        clip_uuid = uuid.uuid4()
                        clip_key = f"projects/{media.project_id}/clips/{clip_uuid}.mp4"

                        file_size = clip_file.stat().st_size
                        with open(clip_file, "rb") as cf:
                            def _cf_gen():
                                while True:
                                    chunk = cf.read(8 * 1024 * 1024)  # 8MB stream chunks
                                    if not chunk:
                                        break
                                    yield chunk
                            storage.save_stream(clip_key, _cf_gen(), file_size)
                            uploaded_keys.append(clip_key)

                        final_clips_to_create.append({
                            "title": clip["title"],
                            "start_time": clip["start_time"],
                            "end_time": clip["end_time"],
                            "reason": clip["reason"],
                            "output_path": clip_key,
                            "subtitle_path": subtitle_key,
                        })

                    # 3. Create database entries in a single commit block
                    for clip_data in final_clips_to_create:
                        self.clip_repository.create(
                            project_id=media.project_id,
                            media_id=media.id,
                            title=clip_data["title"],
                            start_time=clip_data["start_time"],
                            end_time=clip_data["end_time"],
                            reason=clip_data["reason"],
                            output_path=clip_data["output_path"],
                            subtitle_path=clip_data["subtitle_path"],
                        )

            job_manager.update_status(
                job_id,
                JobStatus.COMPLETED,
            )

        except Exception as err:
            traceback.print_exc()

            # Compensation rollback: clean up newly persisted objects in storage upon error
            for key in uploaded_keys:
                try:
                    storage.delete(key)
                except Exception:
                    pass

            job_manager.update_status(
                job_id,
                JobStatus.FAILED,
            )