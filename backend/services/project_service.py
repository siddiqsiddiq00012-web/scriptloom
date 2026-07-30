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

        return self.repository.update_project_name(
            project,
            project_data.name,
        )

    def delete_project(
        self,
        current_user: User,
        project_id: int,
    ) -> None:
        project = self.get_project(
            current_user,
            project_id,
        )

        self.repository.delete_project(project)