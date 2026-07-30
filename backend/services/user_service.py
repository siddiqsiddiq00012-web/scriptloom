from backend.core.security import hash_password, verify_password
from backend.core.token import create_access_token
from backend.models.user import User
from backend.repositories.user_repository import UserRepository
from backend.schemas.user import UserCreate


class UserService:
    def __init__(self, db):
        self.repository = UserRepository(db)

    def register_user(
        self,
        user: UserCreate,
    ) -> User:

        if self.repository.email_exists(user.email):
            raise ValueError("Email already exists.")

        return self.repository.create_user(
            name=user.name,
            email=user.email,
            hashed_password=hash_password(user.password),
        )

    def login(
        self,
        email: str,
        password: str,
    ) -> dict:

        user = self.repository.get_by_email(email)

        if user is None:
            raise ValueError("Invalid email or password.")

        if not verify_password(
            password,
            user.hashed_password,
        ):
            raise ValueError("Invalid email or password.")

        token = create_access_token(
            {
                "sub": user.email,
            }
        )

        return {
            "access_token": token,
            "token_type": "bearer",
        }

    def get_current_user(
        self,
        email: str,
    ) -> User | None:
        return self.repository.get_by_email(email)

    def get_by_id(
        self,
        user_id: int,
    ) -> User | None:
        return self.repository.get_by_id(user_id)

    def get_by_email(
        self,
        email: str,
    ) -> User | None:
        return self.repository.get_by_email(email)