from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.core.dependencies import get_current_user
from backend.db.dependencies import get_db
from backend.models.user import User
from backend.schemas.auth import (
    PasswordResetRequest,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)
from backend.services.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user: UserRegister,
    db: Session = Depends(get_db),
):
    result = AuthService(db).register(user)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered.",
        )

    created_user, token = result

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(created_user),
    )


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db),
):
    result = AuthService(db).login(credentials)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    user, token = result

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.get(
    "/me",
    response_model=UserResponse,
)
def me(
    current_user: User = Depends(get_current_user),
):
    return UserResponse.model_validate(current_user)


@router.post(
    "/forgot-password",
    status_code=status.HTTP_200_OK,
)
def forgot_password(
    data: PasswordResetRequest,
    db: Session = Depends(get_db),
):
    user = AuthService(db).get_user_by_email(data.email)
    # Return success regardless of whether email exists for privacy/security
    return {
        "message": "If the email is registered, a password reset link has been sent."
    }


from pydantic import BaseModel

class GoogleAuthSchema(BaseModel):
    email: str
    name: str = "Google User"
    avatar_url: str | None = None


@router.post(
    "/google",
    response_model=TokenResponse,
)
def google_auth(
    payload: GoogleAuthSchema,
    db: Session = Depends(get_db),
):
    user, token = AuthService(db).google_login(
        email=payload.email,
        name=payload.name,
        avatar_url=payload.avatar_url,
    )
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )