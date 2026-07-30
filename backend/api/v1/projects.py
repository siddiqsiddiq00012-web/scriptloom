from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from backend.auth.security import get_current_user
from backend.db.database import get_db
from backend.models.user import User
from backend.schemas.project import (
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
)
from backend.services.project_service import ProjectService

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_project(
    project: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ProjectService(db)
    return service.create_project(
        current_user=current_user,
        project_data=project,
    )


@router.get(
    "",
    response_model=list[ProjectResponse],
)
def list_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ProjectService(db)
    return service.list_projects(current_user)


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
)
def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ProjectService(db)
    return service.get_project(
        current_user=current_user,
        project_id=project_id,
    )


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
)
def update_project(
    project_id: int,
    project: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ProjectService(db)
    return service.update_project(
        current_user=current_user,
        project_id=project_id,
        project_data=project,
    )


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ProjectService(db)

    service.delete_project(
        current_user=current_user,
        project_id=project_id,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )