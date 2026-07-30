from sqlalchemy.orm import Session

from backend.models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_user(
        self,
        name: str,
        email: str,
        hashed_password: str,
    ) -> User:
        user = User(
            name=name,
            email=email,
            hashed_password=hashed_password,
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def get_by_email(
        self,
        email: str,
    ) -> User | None:
        return (
            self.db.query(User)
            .filter(User.email == email)
            .first()
        )

    def get_by_id(
        self,
        user_id: int,
    ) -> User | None:
        return (
            self.db.query(User)
            .filter(User.id == user_id)
            .first()
        )

    def email_exists(
        self,
        email: str,
    ) -> bool:
        return self.get_by_email(email) is not None

    def update_user(
        self,
        user: User,
        name: str | None = None,
        avatar_url: str | None = None,
        hashed_password: str | None = None,
    ) -> User:
        if name is not None:
            user.name = name
        if avatar_url is not None:
            user.avatar_url = avatar_url
        if hashed_password is not None:
            user.hashed_password = hashed_password

        self.db.commit()
        self.db.refresh(user)
        return user