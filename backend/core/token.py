from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from starlette.requests import Request

from backend.core.config import settings

ACCESS_TOKEN_COOKIE_NAME = "access_token"


def extract_access_token(request: Request) -> str | None:
    """Extract the JWT from the httpOnly cookie or the Authorization header."""
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[7:].strip()

    return request.cookies.get(ACCESS_TOKEN_COOKIE_NAME)


def _get_algorithm() -> str:
    return getattr(settings, "JWT_ALGORITHM", getattr(settings, "ALGORITHM", "HS256"))


def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed JWT access token."""
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + (
        expires_delta
        if expires_delta
        else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=_get_algorithm(),
    )


def verify_access_token(
    token: str,
) -> dict | None:
    """Verify and decode a JWT access token. Returns the payload if valid, otherwise None."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[_get_algorithm()],
        )
        if payload.get("type") == "refresh":
            return None
        return payload
    except JWTError:
        return None


def create_refresh_token(
    data: dict,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed JWT refresh token."""
    to_encode = data.copy()
    to_encode["type"] = "refresh"

    expire = datetime.now(timezone.utc) + (
        expires_delta
        if expires_delta
        else timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=_get_algorithm(),
    )


def verify_refresh_token(
    token: str,
) -> dict | None:
    """Verify and decode a JWT refresh token. Returns the payload if valid, otherwise None."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[_get_algorithm()],
        )
        if payload.get("type") != "refresh":
            return None
        return payload
    except JWTError:
        return None