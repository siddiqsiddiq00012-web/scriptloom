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

    alg = getattr(settings, "JWT_ALGORITHM", getattr(settings, "ALGORITHM", "HS256"))
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=alg,
    )


def verify_access_token(
    token: str,
) -> dict | None:
    try:
        alg = getattr(settings, "JWT_ALGORITHM", getattr(settings, "ALGORITHM", "HS256"))
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[alg],
        )

    except JWTError:
        return None