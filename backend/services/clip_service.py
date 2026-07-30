from sqlalchemy.orm import Session

from backend.models.clip import Clip
from backend.repositories.clip_repository import ClipRepository
from backend.schemas.clip import ClipCreate, ClipUpdate


class ClipService:
    def __init__(self, db: Session):
        self.repository = ClipRepository(db)

    def create_clip(
        self,
        project_id: int,
        clip_data: ClipCreate,
    ) -> Clip:

        if clip_data.end_time <= clip_data.start_time:
            raise ValueError(
                "end_time must be greater than start_time"
            )

        clip = Clip(
            project_id=project_id,
            media_id=clip_data.media_id,
            title=clip_data.title,
            start_time=clip_data.start_time,
            end_time=clip_data.end_time,
            status="pending",
            output_path=None,
        )

        return self.repository.create(clip)

    def get_clip(
        self,
        clip_id: int,
    ) -> Clip | None:
        return self.repository.get_by_id(clip_id)

    def list_project_clips(
        self,
        project_id: int,
    ) -> list[Clip]:
        return self.repository.get_project_clips(project_id)

    def update_clip(
        self,
        clip_id: int,
        data: ClipUpdate,
    ) -> Clip:

        clip = self.repository.get_by_id(clip_id)

        if clip is None:
            raise ValueError("Clip not found")

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(clip, field, value)

        if clip.end_time <= clip.start_time:
            raise ValueError(
                "end_time must be greater than start_time"
            )

        return self.repository.update(clip)

    def delete_clip(
        self,
        clip_id: int,
    ) -> None:

        clip = self.repository.get_by_id(clip_id)

        if clip is None:
            raise ValueError("Clip not found")

        self.repository.delete(clip)