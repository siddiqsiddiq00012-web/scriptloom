from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.schemas.user import (
    Token,
    UserCreate,
    UserLogin,
    UserResponse,
)
from backend.services.user_service import UserService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    service = UserService(db)
    return service.register_user(user)


@router.post(
    "/login",
    response_model=Token,
)
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db),
):
    service = UserService(db)
    return service.login(
        credentials.email,
        credentials.password,
    )