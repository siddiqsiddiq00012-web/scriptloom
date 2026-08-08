import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from google.oauth2 import id_token
from google.auth.transport import requests

from backend.core.config import settings
from backend.core.dependencies import get_current_user
from backend.db.dependencies import get_db
from backend.models.user import User
from backend.schemas.auth import (
    PasswordResetRequest,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
    GoogleAuthRequest,
)
from backend.services.auth_service import AuthService

logger = logging.getLogger("scriptloom.auth")

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
    try:
        result = AuthService(db).register(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered.",
        )

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

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has been deactivated. Please contact support.",
        )

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


@router.post(
    "/google",
    response_model=TokenResponse,
)
def google_auth(
    payload: GoogleAuthRequest,
    db: Session = Depends(get_db),
):
    # 1. Ensure GOOGLE_CLIENT_ID is configured on the server
    if not settings.GOOGLE_CLIENT_ID:
        logger.error("GOOGLE_CLIENT_ID is not configured in settings.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google OAuth configuration is missing on the server.",
        )

    # 2. Extract token from payload
    try:
        token = payload.get_token
    except ValueError as e:
        logger.warning(f"Google auth request missing token: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google ID Token is required.",
        )

    # 3. Verify the Google ID token
    try:
        # id_token.verify_oauth2_token verifies signature, audience, and expiration.
        id_info = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            audience=settings.GOOGLE_CLIENT_ID,
        )
    except Exception as e:
        logger.error(f"Google ID Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed. Please verify your credentials.",
        )

    # 4. Verify the Issuer (iss claim) explicitly
    issuer = id_info.get("iss")
    if issuer not in ["accounts.google.com", "https://accounts.google.com"]:
        logger.error(f"Google ID Token has invalid issuer: {issuer}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed. Please verify your credentials.",
        )

    # 5. Check email verification (email_verified claim)
    if not id_info.get("email_verified"):
        logger.error("Google ID Token email is not verified.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed. Please verify your credentials.",
        )

    # 6. Extract claims (email, name, picture)
    email = id_info.get("email")
    if not email:
        logger.error("Google ID Token claims do not include email.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed. Please verify your credentials.",
        )

    name = id_info.get("name", email.split("@")[0])
    avatar_url = id_info.get("picture")

    # 7. Authenticate or register the user
    user, jwt_token = AuthService(db).google_login(
        email=email,
        name=name,
        avatar_url=avatar_url,
    )

    return TokenResponse(
        access_token=jwt_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )