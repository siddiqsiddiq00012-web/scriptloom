from sqlalchemy.orm import Session

from backend.models.media import Media
from backend.schemas.video_metadata import VideoMetadata


class MediaRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_media(
        self,
        *,
        project_id: int,
        filename: str,
        storage_path: str,
        file_size: int,
        metadata: VideoMetadata,
    ) -> Media:

        media = Media(
            project_id=project_id,
            filename=filename,
            storage_path=storage_path,
            file_size=file_size,
            status="uploaded",
            duration=metadata.duration,
            width=metadata.width,
            height=metadata.height,
            codec=metadata.codec,
            bitrate=metadata.bitrate,
            fps=metadata.fps,
        )

        self.db.add(media)
        self.db.commit()
        self.db.refresh(media)

        return media

    def get_by_project(
        self,
        project_id: int,
    ) -> list[Media]:
        return (
            self.db.query(Media)
            .filter(Media.project_id == project_id)
            .all()
        )

    def get_by_id(
        self,
        media_id: int,
    ) -> Media | None:
        return (
            self.db.query(Media)
            .filter(Media.id == media_id)
            .first()
        )

    def get_by_path(
        self,
        storage_path: str,
    ) -> Media | None:
        return (
            self.db.query(Media)
            .filter(Media.storage_path == storage_path)
            .first()
        )