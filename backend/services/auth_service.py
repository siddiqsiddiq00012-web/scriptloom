from sqlalchemy.orm import Session

from backend.core.security import (
    hash_password,
    verify_password,
)
from backend.core.token import create_access_token, create_refresh_token
from backend.repositories.user_repository import UserRepository
from backend.schemas.auth import UserLogin, UserRegister


class AuthService:
    def __init__(self, db: Session):
        self.users = UserRepository(db)

    def _issue_tokens(self, user_id: int) -> tuple[str, str]:
        access_token = create_access_token({"sub": str(user_id)})
        refresh_token = create_refresh_token({"sub": str(user_id)})
        return access_token, refresh_token

    def register(
        self,
        user_data: UserRegister,
    ) -> tuple | None:
        existing_user = self.users.get_by_email(
            user_data.email,
        )

        if existing_user:
            return None

        created_user = self.users.create_user(
            name=user_data.name,
            email=user_data.email,
            hashed_password=hash_password(
                user_data.password,
            ),
        )

        access_token, refresh_token = self._issue_tokens(created_user.id)

        return created_user, access_token, refresh_token

    def login(
        self,
        credentials: UserLogin,
    ) -> tuple | None:
        user = self.users.get_by_email(
            credentials.email,
        )

        if user is None:
            return None

        if not verify_password(
            credentials.password,
            user.hashed_password,
        ):
            return None

        access_token, refresh_token = self._issue_tokens(user.id)

        return user, access_token, refresh_token

    def refresh(
        self,
        refresh_token: str,
    ) -> tuple | None:
        from backend.core.token import verify_refresh_token

        payload = verify_refresh_token(refresh_token)
        if payload is None:
            return None

        user_id = payload.get("sub")
        if user_id is None:
            return None

        user = self.users.get_by_id(int(user_id))
        if user is None:
            return None

        access_token, new_refresh_token = self._issue_tokens(user.id)
        return user, access_token, new_refresh_token

    def google_login(
        self,
        email: str,
        name: str = "Google User",
        avatar_url: str = None,
    ) -> tuple:
        user = self.users.get_by_email(email)

        if user is None:
            # Create user in DB with a random unverifiable password hash
            # so they cannot be logged in via the password-based login flow.
            import secrets
            random_pass = secrets.token_urlsafe(32)
            user = self.users.create_user(
                name=name,
                email=email,
                hashed_password=hash_password(random_pass),
            )
            if avatar_url and hasattr(user, "avatar_url"):
                user.avatar_url = avatar_url
                self.users.db.commit()

        access_token, refresh_token = self._issue_tokens(user.id)
        return user, access_token, refresh_token

    def get_user_by_email(
        self,
        email: str,
    ):
        return self.users.get_by_email(email)
