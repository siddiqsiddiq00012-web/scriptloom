import logging
import secrets
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from google.oauth2 import id_token
from google.auth.transport import requests

from backend.core.config import settings
from backend.core.dependencies import get_current_user
from backend.db.dependencies import get_db
from backend.models.user import User
from backend.schemas.auth import (
    PasswordResetConfirmRequest,
    PasswordResetRequest,
    TokenRefreshRequest,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
    GoogleAuthRequest,
)
from backend.services.auth_service import AuthService
from backend.services.email_service import EmailDeliveryError
from backend.services.password_reset_service import PasswordResetService

logger = logging.getLogger("scriptloom.auth")

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

COOKIE_NAME = "access_token"
SESSION_COOKIE_NAME = "session_active"
CSRF_COOKIE_NAME = "csrf_token"
CSRF_HEADER = "X-CSRF-Token"


def _set_auth_cookie(response: Response, token: str):
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )
    # Non-httpOnly session flag so the SPA can cheaply detect auth state.
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value="1",
        httponly=False,
        secure=not settings.DEBUG,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )


def _clear_auth_cookie(response: Response):
    response.delete_cookie(key=COOKIE_NAME, path="/")
    response.delete_cookie(key=SESSION_COOKIE_NAME, path="/")


def _set_csrf_cookie(response: Response):
    csrf = secrets.token_urlsafe(32)
    response.set_cookie(
        key=CSRF_COOKIE_NAME,
        value=csrf,
        httponly=False,
        secure=not settings.DEBUG,
        samesite="lax",
        path="/",
    )
    return csrf


def _build_token_response(response: Response, user: User, access_token: str, refresh_token: str) -> TokenResponse:
    _set_auth_cookie(response, access_token)
    _set_csrf_cookie(response)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.get("/csrf-token")
def get_csrf_token(response: Response):
    csrf = _set_csrf_cookie(response)
    return {"csrf_token": csrf}


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
def logout(response: Response):
    _clear_auth_cookie(response)
    return None


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user: UserRegister,
    response: Response,
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

    created_user, token, refresh_token = result

    return _build_token_response(response, created_user, token, refresh_token)


@router.post(
    "/refresh",
    response_model=TokenResponse,
)
def refresh(
    data: TokenRefreshRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    result = AuthService(db).refresh(data.refresh_token)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token.",
        )

    user, token, refresh_token = result

    return _build_token_response(response, user, token, refresh_token)


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    credentials: UserLogin,
    response: Response,
    db: Session = Depends(get_db),
):
    result = AuthService(db).login(credentials)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    user, token, refresh_token = result

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has been deactivated. Please contact support.",
        )

    return _build_token_response(response, user, token, refresh_token)


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
    try:
        PasswordResetService(db).request_reset(data.email)
    except EmailDeliveryError as e:
        # Deliberately generic: the response must not reveal whether an
        # account exists for the given email (anti-enumeration).
        logger.error(f"Password reset request failed: {e}")
    return {
        "message": (
            "If an account exists for that email, a password reset link "
            "has been sent."
        )
    }


@router.post(
    "/reset-password",
    status_code=status.HTTP_200_OK,
)
def reset_password(
    data: PasswordResetConfirmRequest,
    db: Session = Depends(get_db),
):
    success = PasswordResetService(db).reset_password(
        data.token,
        data.new_password,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This password reset link is invalid or has expired.",
        )
    return {"message": "Your password has been updated. Please sign in."}


@router.post(
    "/google",
    response_model=TokenResponse,
)
def google_auth(
    payload: GoogleAuthRequest,
    response: Response,
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
    user, jwt_token, refresh_token = AuthService(db).google_login(
        email=email,
        name=name,
        avatar_url=avatar_url,
    )

    return _build_token_response(response, user, jwt_token, refresh_token)