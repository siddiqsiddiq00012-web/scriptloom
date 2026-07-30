from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.dependencies import get_current_user
from backend.db.dependencies import get_db
from backend.models.user import User
from backend.repositories.user_repository import UserRepository
from backend.schemas.auth import ProfileUpdate, UserResponse

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "/me",
    response_model=UserResponse,
)
def read_me(
    current_user: User = Depends(get_current_user),
):
    return UserResponse.model_validate(current_user)


@router.put(
    "/me",
    response_model=UserResponse,
)
def update_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repository = UserRepository(db)
    updated_user = repository.update_user(
        user=current_user,
        name=profile_data.name,
        avatar_url=profile_data.avatar_url,
    )
    return UserResponse.model_validate(updated_user)