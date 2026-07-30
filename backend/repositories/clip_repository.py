from sqlalchemy.orm import Session

from backend.models.clip import Clip


class ClipRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        *,
        project_id: int,
        media_id: int,
        title: str,
        start_time: float,
        end_time: float,
        reason: str,
        output_path: str,
        subtitle_path: str,
    ) -> Clip:
        clip = Clip(
            project_id=project_id,
            media_id=media_id,
            title=title,
            start_time=start_time,
            end_time=end_time,
            reason=reason,
            output_path=output_path,
            subtitle_path=subtitle_path,
        )

        self.db.add(clip)
        self.db.commit()
        self.db.refresh(clip)

        return clip

    def get_by_id(
        self,
        clip_id: int,
    ) -> Clip | None:
        return (
            self.db.query(Clip)
            .filter(Clip.id == clip_id)
            .first()
        )

    def get_project_clips(
        self,
        project_id: int,
    ) -> list[Clip]:
        return (
            self.db.query(Clip)
            .filter(Clip.project_id == project_id)
            .all()
        )

    def update(
        self,
        clip: Clip,
    ) -> Clip:
        self.db.commit()
        self.db.refresh(clip)
        return clip

    def delete(
        self,
        clip: Clip,
    ) -> None:
        self.db.delete(clip)
        self.db.commit()