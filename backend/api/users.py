from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.core.dependencies import get_current_user
from backend.core.security import verify_password, hash_password
from backend.db.dependencies import get_db
from backend.models.user import User
from backend.repositories.user_repository import UserRepository
from backend.schemas.auth import ProfileUpdate, UserResponse, PasswordChangeRequest

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "/me",
    response_model=UserResponse,
)
def read_me(
    current_user: User = Depends(get_current_user),
):
    return UserResponse.model_validate(current_user)


@router.put(
    "/me",
    response_model=UserResponse,
)
def update_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repository = UserRepository(db)
    updated_user = repository.update_user(
        user=current_user,
        name=profile_data.name,
        avatar_url=profile_data.avatar_url,
    )

    # Update additional profile fields
    if profile_data.bio is not None:
        updated_user.bio = profile_data.bio
    if profile_data.company is not None:
        updated_user.company = profile_data.company
    if profile_data.role is not None:
        updated_user.role = profile_data.role
    if profile_data.timezone is not None:
        updated_user.timezone = profile_data.timezone

    db.commit()
    db.refresh(updated_user)
    return UserResponse.model_validate(updated_user)


@router.post(
    "/me/change-password",
    status_code=status.HTTP_200_OK,
)
def change_password(
    data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Change the current user's password."""
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect.",
        )

    current_user.hashed_password = hash_password(data.new_password)
    db.commit()

    return {"message": "Password changed successfully."}


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete the current user's account and all associated data."""
    db.delete(current_user)
    db.commit()


@router.get(
    "/me/export",
)
def export_account_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Export the current user's account data as JSON."""
    from backend.models.project import Project
    from backend.models.media import Media
    from backend.models.generated_content import GeneratedContent

    projects = db.query(Project).filter(Project.owner_id == current_user.id).all()
    project_data = []
    for p in projects:
        media_items = db.query(Media).filter(Media.project_id == p.id).all()
        media_data = []
        for m in media_items:
            generated = db.query(GeneratedContent).filter(GeneratedContent.media_id == m.id).all()
            media_data.append({
                "id": m.id,
                "filename": m.filename,
                "status": m.status,
                "duration": m.duration,
                "created_at": str(m.created_at) if m.created_at else None,
                "generated_content_count": len(generated),
            })
        project_data.append({
            "id": p.id,
            "name": p.name,
            "created_at": str(p.created_at) if p.created_at else None,
            "media_count": len(media_data),
            "media": media_data,
        })

    return {
        "user": {
            "name": current_user.name,
            "email": current_user.email,
            "bio": current_user.bio,
            "company": current_user.company,
            "role": current_user.role,
            "timezone": current_user.timezone,
            "created_at": str(current_user.created_at) if current_user.created_at else None,
        },
        "projects": project_data,
        "exported_at": str(__import__("datetime").datetime.utcnow()),
    }
