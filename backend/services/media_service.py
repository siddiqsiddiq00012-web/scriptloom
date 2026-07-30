from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.models.media import Media
from backend.models.user import User
from backend.repositories.media_repository import MediaRepository
from backend.services.project_service import ProjectService


class MediaService:
    def __init__(self, db: Session):
        self.db = db
        self.media_repository = MediaRepository(db)
        self.project_service = ProjectService(db)

    def create_media(
        self,
        current_user: User,
        project_id: int,
        filename: str,
        storage_path: str,
        file_size: int,
    ) -> Media:
        # Verify that the project belongs to the current user
        self.project_service.get_project(
            current_user=current_user,
            project_id=project_id,
        )

        return self.media_repository.create_media(
            project_id=project_id,
            filename=filename,
            storage_path=storage_path,
            file_size=file_size,
        )

    def list_media(
        self,
        current_user: User,
        project_id: int,
    ) -> list[Media]:
        # Verify project ownership
        self.project_service.get_project(
            current_user=current_user,
            project_id=project_id,
        )

        return self.media_repository.get_by_project(
            project_id=project_id,
        )

    def get_media(
        self,
        current_user: User,
        project_id: int,
        media_id: int,
    ) -> Media:
        # Verify project ownership
        self.project_service.get_project(
            current_user=current_user,
            project_id=project_id,
        )

        media = self.media_repository.get_by_id(
            media_id,
        )

        if media is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Media not found.",
            )

        if media.project_id != project_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Media not found.",
            )

        return media