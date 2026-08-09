import hashlib
import logging
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.core.security import hash_password
from backend.models.password_reset_token import PasswordResetToken
from backend.repositories.user_repository import UserRepository
from backend.services.email_service import (
    EmailDeliveryError,
    send_password_reset_email,
)

logger = logging.getLogger("scriptloom.password_reset")


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class PasswordResetService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)

    def request_reset(self, email: str) -> None:
        """Issue a single-use reset token and email its link.

        The response must not reveal whether the account exists, so an
        unknown email is handled identically from the caller's perspective
        (no token is created and no email is sent).
        """
        user = self.users.get_by_email(email)
        if user is None:
            return

        now = _utcnow()

        # Invalidate any previously issued, still-unused tokens for this user.
        self.db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.used_at.is_(None),
        ).update({"used_at": now})

        token = secrets.token_urlsafe(32)
        token_row = PasswordResetToken(
            user_id=user.id,
            token_hash=_hash_token(token),
            expires_at=now
            + timedelta(minutes=settings.PASSWORD_RESET_TOKEN_TTL_MINUTES),
        )
        self.db.add(token_row)
        self.db.commit()

        reset_url = (
            f"{settings.FRONTEND_URL.rstrip('/')}/reset-password?token={token}"
        )

        try:
            send_password_reset_email(user.email, reset_url)
        except EmailDeliveryError:
            # Do not leave a dangling valid token behind when delivery fails;
            # a retry should mint a fresh one.
            logger.error(
                f"Password reset email delivery failed for user {user.id}; "
                "revoking issued token."
            )
            self.db.query(PasswordResetToken).filter(
                PasswordResetToken.id == token_row.id
            ).delete()
            self.db.commit()
            raise

    def reset_password(self, token: str, new_password: str) -> bool:
        """Consume a valid reset token and change the user's password.

        Returns False for any invalid, expired, or already-used token without
        distinguishing the reason, so callers expose only a generic message.
        """
        token_row = (
            self.db.query(PasswordResetToken)
            .filter(PasswordResetToken.token_hash == _hash_token(token))
            .first()
        )
        if token_row is None:
            return False

        if token_row.used_at is not None:
            return False

        expires_at = token_row.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < _utcnow():
            return False

        user = self.users.get_by_id(token_row.user_id)
        if user is None:
            return False

        self.users.update_user(
            user,
            hashed_password=hash_password(new_password),
        )

        now = _utcnow()
        token_row.used_at = now

        # Invalidate every other outstanding token for this user.
        self.db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.id != token_row.id,
            PasswordResetToken.used_at.is_(None),
        ).update({"used_at": now})

        self.db.commit()
        logger.info(f"Password reset completed for user {user.id}.")
        return True
