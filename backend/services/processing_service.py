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
from backend.events.event_bus import event_bus, EventSchema, ProgressState


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

        job = job_manager.create_job(self.db, media_id, user_id)

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
    ) -> None:
        """
        Execute the processing pipeline.
        """
        uploaded_keys = []

        # Publish progress events to the in-process EventBus, which fans out
        # to SSE clients subscribed via /stream/progress/{media_id}.
        def publish_progress(state: str, payload: dict = None):
            try:
                event_bus.publish(
                    EventSchema(
                        event_type=f"media.processing.{state}",
                        user_id=self._job_user_id if hasattr(self, "_job_user_id") else None,
                        media_id=self._job_media_id if hasattr(self, "_job_media_id") else None,
                        payload={
                            "job_id": job_id,
                            "state": state,
                            **(payload or {}),
                        },
                    )
                )
            except Exception as exc:
                print(f"[EVENT PUBLISH ERROR] {state}: {exc}")

        try:
            job_manager.update_status(
                self.db,
                job_id,
                JobStatus.PROCESSING,
            )

            # video_path here is the media.storage_path key
            media = self.media_repository.get_by_path(video_path)

            if media is None:
                raise RuntimeError("Media record not found.")

            self._job_user_id = media.user_id
            self._job_media_id = media.id

            publish_progress("started", {"media_id": media.id})

            # A. Materialize the remote/local file context
            with storage.materialize(media.storage_path) as materialized_video_path:
                # B. Create temporary directory for FFmpeg workspace
                with tempfile.TemporaryDirectory(prefix="process_job_") as temp_dir_str:
                    temp_output_dir = Path(temp_dir_str)

                    pipeline = ProcessingPipeline()
                    generated_clips = pipeline.process_video(
                        video_path=str(materialized_video_path),
                        output_directory=str(temp_output_dir),
                        progress_callback=lambda state, payload: publish_progress(state, payload),
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
                self.db,
                job_id,
                JobStatus.COMPLETED,
            )

            publish_progress("completed", {
                "clips": len(final_clips_to_create),
            })

        except Exception as err:
            traceback.print_exc()

            publish_progress("failed", {"error": str(err)})

            # Compensation rollback: clean up newly persisted objects in storage upon error
            for key in uploaded_keys:
                try:
                    storage.delete(key)
                except Exception:
                    pass

            # Update status to FAILED in current session before propagating
            try:
                job_manager.update_status(
                    self.db,
                    job_id,
                    JobStatus.FAILED,
                )
            except Exception:
                pass
            raise err