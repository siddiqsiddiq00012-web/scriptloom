from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.db.dependencies import get_db
from backend.repositories.user_repository import UserRepository
from backend.models.user import User
from backend.models.project import Project
from backend.models.media import Media
from backend.models.transcript import Transcript, TranscriptSegment
from backend.models.generated_content import GeneratedContent
from backend.models.clip import Clip
from backend.models.webhook import WebhookEndpoint

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

    except (JWTError, ValueError):
        raise credentials_exception

    repository = UserRepository(db)

    try:
        user = repository.get_by_id(int(user_id))
    except (ValueError, TypeError):
        raise credentials_exception

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated.",
        )

    return user


def verify_project_ownership(
    project_id: int,
    user: User,
    db: Session,
) -> Project:
    project = (
        db.query(Project)
        .filter(Project.id == project_id, Project.owner_id == user.id)
        .first()
    )
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found."
        )
    return project


def verify_media_ownership(
    media_id: int,
    user: User,
    db: Session,
) -> Media:
    media = (
        db.query(Media)
        .join(Project, Media.project_id == Project.id)
        .filter(Media.id == media_id, Project.owner_id == user.id)
        .first()
    )
    if media is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media not found."
        )
    return media


def verify_content_ownership(
    content_id: int,
    user: User,
    db: Session,
) -> GeneratedContent:
    content = (
        db.query(GeneratedContent)
        .join(Project, GeneratedContent.project_id == Project.id)
        .filter(GeneratedContent.id == content_id, Project.owner_id == user.id)
        .first()
    )
    if content is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generated content not found."
        )
    return content


def verify_segment_ownership(
    segment_id: int,
    user: User,
    db: Session,
) -> TranscriptSegment:
    segment = (
        db.query(TranscriptSegment)
        .join(Transcript, TranscriptSegment.transcript_id == Transcript.id)
        .join(Media, Transcript.media_id == Media.id)
        .join(Project, Media.project_id == Project.id)
        .filter(TranscriptSegment.id == segment_id, Project.owner_id == user.id)
        .first()
    )
    if segment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transcript segment not found."
        )
    return segment


def verify_clip_ownership(
    clip_id: int,
    user: User,
    db: Session,
) -> Clip:
    clip = (
        db.query(Clip)
        .join(Project, Clip.project_id == Project.id)
        .filter(Clip.id == clip_id, Project.owner_id == user.id)
        .first()
    )
    if clip is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clip not found."
        )
    return clip


def verify_webhook_endpoint_ownership(
    endpoint_id: int,
    user: User,
    db: Session,
) -> WebhookEndpoint:
    endpoint = (
        db.query(WebhookEndpoint)
        .filter(WebhookEndpoint.id == endpoint_id, WebhookEndpoint.user_id == user.id)
        .first()
    )
    if endpoint is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook endpoint not found."
        )
    return endpoint