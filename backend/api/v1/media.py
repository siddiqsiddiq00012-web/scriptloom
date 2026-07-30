from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from backend.auth.security import get_current_user
from backend.db.database import get_db
from backend.models.user import User
from backend.schemas.media import MediaResponse
from backend.services.media_service import MediaService
from backend.services.storage_service import StorageService

router = APIRouter(
    prefix="/projects/{project_id}/media",
    tags=["Media"],
)


@router.post(
    "",
    response_model=MediaResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_media(
    project_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    storage = StorageService()

    filename, storage_path, file_size = storage.save_file(
        project_id=project_id,
        file=file,
    )

    service = MediaService(db)

    return service.create_media(
        current_user=current_user,
        project_id=project_id,
        filename=filename,
        storage_path=storage_path,
        file_size=file_size,
    )