from sqlalchemy.orm import Session

from backend.core.security import (
    hash_password,
    verify_password,
)
from backend.core.token import create_access_token
from backend.repositories.user_repository import UserRepository
from backend.schemas.auth import UserLogin, UserRegister


class AuthService:
    def __init__(self, db: Session):
        self.users = UserRepository(db)

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

        token = create_access_token(
            {
                "sub": str(created_user.id),
            }
        )

        return created_user, token

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

        token = create_access_token(
            {
                "sub": str(user.id),
            }
        )

        return user, token

    def get_user_by_email(
        self,
        email: str,
    ):
        return self.users.get_by_email(email)