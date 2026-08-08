from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.models.project import Project
from backend.models.user import User
from backend.repositories.project_repository import ProjectRepository
from backend.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    def __init__(self, db: Session):
        self.repository = ProjectRepository(db)

    def create_project(
        self,
        current_user: User,
        project_data: ProjectCreate,
    ) -> Project:
        return self.repository.create_project(
            owner_id=current_user.id,
            name=project_data.name,
        )

    def list_projects(
        self,
        current_user: User,
    ) -> list[Project]:
        return self.repository.get_all_by_owner(
            current_user.id,
        )

    def get_project(
        self,
        current_user: User,
        project_id: int,
    ) -> Project:
        project = self.repository.get_by_id_and_owner(
            project_id,
            current_user.id,
        )

        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found.",
            )

        return project

    def update_project(
        self,
        current_user: User,
        project_id: int,
        project_data: ProjectUpdate,
    ) -> Project:
        project = self.get_project(
            current_user,
            project_id,
        )

        if project_data.name is not None:
            project = self.repository.update_project_name(
                project,
                project_data.name,
            )

        return project

    def delete_project(
        self,
        current_user: User,
        project_id: int,
    ) -> None:
        project = self.get_project(
            current_user,
            project_id,
        )

        db = self.repository.db

        # 2. Collect all descendant persistent media/clip/waveform objects before changing database state
        from backend.models.media import Media
        from backend.models.clip import Clip
        from backend.storage.base import validate_storage_key
        from backend.storage.manager import storage

        media_items = db.query(Media).filter(Media.project_id == project.id).all()
        keys_to_delete = []
        for media in media_items:
            if media.storage_path:
                keys_to_delete.append(media.storage_path)

            waveform_key = f"projects/{media.project_id}/waveforms/{media.id}_waveform.json"
            keys_to_delete.append(waveform_key)

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
            self.repository.delete_project(project)
        except Exception as db_err:
            # 6. Rollback DB and log inconsistency
            db.rollback()
            print(f"[DATABASE INCONSISTENCY ERROR] DB project delete failed after storage objects were deleted: {str(db_err)}")
            raise HTTPException(
                status_code=500,
                detail="Database record deletion failed. Storage state may be inconsistent.",
            )