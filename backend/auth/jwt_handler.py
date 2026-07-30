from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from backend.core.config import settings


def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None,
) -> str:
    to_encode = data.copy()

    expire = (
        datetime.now(timezone.utc)
        + (
            expires_delta
            if expires_delta
            else timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        )
    )

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def verify_access_token(
    token: str,
) -> dict | None:
    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )

    except JWTError:
        return None