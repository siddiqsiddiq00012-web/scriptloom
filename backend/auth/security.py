from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from backend.core.token import verify_access_token
from backend.db.dependencies import get_db
from backend.models.user import User
from backend.services.user_service import UserService

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials

    print("\n" + "=" * 60)
    print("TOKEN:")
    print(token)

    payload = verify_access_token(token)

    print("\nPAYLOAD:")
    print(payload)

    if payload is None:
        print("\nFAILED: Token verification failed.")
        print("=" * 60)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )

    user_id = payload.get("sub")

    print("\nUSER ID:")
    print(user_id)

    if user_id is None:
        print("\nFAILED: 'sub' claim missing.")
        print("=" * 60)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload.",
        )

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        print("\nFAILED: Invalid user ID in token.")
        print("=" * 60)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload.",
        )

    service = UserService(db)
    user = service.get_by_id(user_id)

    print("\nUSER:")
    print(user)

    if user is None:
        print("\nFAILED: User not found.")
        print("=" * 60)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
        )

    print("\nSUCCESS: Authentication passed.")
    print("=" * 60)

    return user