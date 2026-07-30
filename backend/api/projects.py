from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.auth.security import get_current_user
from backend.db.dependencies import get_db
from backend.models.user import User
from backend.schemas.project import (
    ProjectCreate,
    ProjectResponse,
)
from backend.services.project_service import ProjectService

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)


@router.post(
    "/",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ProjectService(db).create_project(
        current_user=current_user,
        project_data=project,
    )


@router.get(
    "/",
    response_model=list[ProjectResponse],
)
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ProjectService(db).list_projects(
        current_user=current_user,
    )