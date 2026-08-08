from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.core.dependencies import (
    get_current_user,
    verify_media_ownership,
    verify_content_ownership,
)
from backend.db.dependencies import get_db
from backend.models.user import User
from backend.models.generated_content import GeneratedContent
from backend.schemas.generation import (
    CampaignPackResponse,
    ContentUpdate,
    GeneratedContentResponse,
    ContentGenerationRequest,
    ContentTypeOption,
)
from backend.services.generation_engine import GenerationEngine
from backend.services.content_generator import (
    ContentGenerator,
    SUPPORTED_CONTENT_TYPES,
    CONTENT_TYPE_CONFIGS,
)
from backend.services.billing_service import BillingService
from backend.services.feature_gate import Feature

router = APIRouter(
    prefix="/generation",
    tags=["AI Generation"],
)

# Content type metadata for the frontend
CONTENT_TYPE_OPTIONS = [
    ContentTypeOption(key="linkedin_post", label="LinkedIn Post", description="Professional LinkedIn post based on your content", category="social", available=True),
    ContentTypeOption(key="x_thread", label="X Thread", description="Twitter/X thread with tweet breakdown", category="social", available=True),
    ContentTypeOption(key="instagram_caption", label="Instagram Caption", description="Engaging Instagram caption with hashtags", category="social", available=True),
    ContentTypeOption(key="newsletter", label="Newsletter", description="Email newsletter in markdown format", category="long_form", available=True),
    ContentTypeOption(key="article", label="Blog Article", description="SEO-friendly blog article", category="long_form", available=True),
    ContentTypeOption(key="video_script", label="Video Script", description="Short-form video script with visual cues", category="long_form", available=True),
    ContentTypeOption(key="hook", label="Content Hooks", description="10 powerful opening hooks for social/email", category="ideas", available=True),
    ContentTypeOption(key="title", label="Titles & Headlines", description="10 title options in various styles", category="ideas", available=True),
    ContentTypeOption(key="content_idea", label="Content Ideas", description="8 content ideas with platform suggestions", category="ideas", available=True),
]


@router.post(
    "/campaign-pack/{media_id}",
    response_model=CampaignPackResponse,
    status_code=status.HTTP_201_CREATED,
)
def generate_campaign_pack(
    media_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Verify media ownership before triggering expensive AI generation
    verify_media_ownership(media_id, current_user, db)

    engine = GenerationEngine(db)
    try:
        assets = engine.generate_campaign_pack(media_id)
        if not assets:
            raise HTTPException(
                status_code=400,
                detail="Failed to generate campaign pack assets",
            )

        asset_responses = [GeneratedContentResponse.model_validate(a) for a in assets]
        return CampaignPackResponse(
            media_id=media_id,
            project_id=assets[0].project_id,
            count=len(assets),
            assets=asset_responses,
        )
    except ValueError as val_err:
        raise HTTPException(
            status_code=400,
            detail=str(val_err),
        )


@router.get(
    "/campaign-pack/{media_id}",
    response_model=CampaignPackResponse,
)
def get_campaign_pack(
    media_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Verify media ownership before fetching campaign pack
    verify_media_ownership(media_id, current_user, db)

    assets = (
        db.query(GeneratedContent)
        .filter(GeneratedContent.media_id == media_id)
        .order_by(GeneratedContent.id)
        .all()
    )

    if not assets:
        raise HTTPException(
            status_code=404,
            detail="No campaign pack generated for this media. Call POST /generation/campaign-pack/{media_id} first.",
        )

    asset_responses = [GeneratedContentResponse.model_validate(a) for a in assets]
    return CampaignPackResponse(
        media_id=media_id,
        project_id=assets[0].project_id,
        count=len(assets),
        assets=asset_responses,
    )


@router.put(
    "/content/{content_id}",
    response_model=GeneratedContentResponse,
)
def update_generated_content(
    content_id: int,
    update_data: ContentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Verify content asset ownership before editing
    asset = verify_content_ownership(content_id, current_user, db)

    if update_data.title is not None:
        asset.title = update_data.title
    if update_data.body_json is not None:
        asset.body_json = update_data.body_json

    db.commit()
    db.refresh(asset)
    return GeneratedContentResponse.model_validate(asset)


@router.get(
    "/content-types",
    response_model=list[ContentTypeOption],
)
def list_content_types():
    """Return available content types and their metadata for the frontend."""
    return CONTENT_TYPE_OPTIONS


@router.post(
    "/media/{media_id}/generate",
    response_model=GeneratedContentResponse,
    status_code=status.HTTP_201_CREATED,
)
def generate_content_for_media(
    media_id: int,
    request: ContentGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate a single content asset from a specific media resource using AI."""
    verify_media_ownership(media_id, current_user, db)

    # Check AI generation quota before calling the LLM
    billing_service = BillingService(db)
    billing_service.check_quota(current_user, Feature.AI_GENERATIONS, additional=1)

    generator = ContentGenerator(db)
    try:
        asset = generator.generate(
            media_id=media_id,
            content_type=request.content_type,
            tone=request.tone,
            audience=request.audience,
            length=request.length,
            extra_instructions=request.extra_instructions,
        )
        # Record AI generation usage after successful generation
        billing_service.record_usage(current_user, ai_generations=1)
        return GeneratedContentResponse.model_validate(asset)
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err),
        )
    except RuntimeError as rt_err:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(rt_err),
        )


@router.get(
    "/media/{media_id}/content",
)
def get_media_content(
    media_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all generated content for a media, grouped by content_type with counts."""
    verify_media_ownership(media_id, current_user, db)

    assets = (
        db.query(GeneratedContent)
        .filter(GeneratedContent.media_id == media_id)
        .order_by(GeneratedContent.id)
        .all()
    )

    # Group by content_type
    grouped: dict[str, list[GeneratedContentResponse]] = {}
    for asset in assets:
        ct = asset.content_type
        if ct not in grouped:
            grouped[ct] = []
        grouped[ct].append(GeneratedContentResponse.model_validate(asset))

    return {
        "media_id": media_id,
        "total_count": len(assets),
        "by_type": grouped,
    }


@router.delete(
    "/content/{content_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_generated_content(
    content_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a generated content asset."""
    asset = verify_content_ownership(content_id, current_user, db)
    db.delete(asset)
    db.commit()


@router.get("/library")
def get_content_library(
    content_type: str | None = None,
    project_id: int | None = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return all generated content across all projects, filterable by type."""
    from backend.models.project import Project
    from backend.models.media import Media

    user_project_ids = [p.id for p in db.query(Project.id).filter(Project.owner_id == current_user.id).all()]

    query = (
        db.query(GeneratedContent)
        .filter(GeneratedContent.project_id.in_(user_project_ids))
        .order_by(GeneratedContent.created_at.desc())
    )

    if content_type:
        query = query.filter(GeneratedContent.content_type == content_type)
    if project_id and project_id in user_project_ids:
        query = query.filter(GeneratedContent.project_id == project_id)

    total = query.count()
    assets = query.offset(offset).limit(limit).all()

    result = []
    for asset in assets:
        media = db.get(Media, asset.media_id) if asset.media_id else None
        result.append({
            "id": asset.id,
            "content_type": asset.content_type,
            "title": asset.title,
            "body_json": asset.body_json,
            "status": asset.status,
            "created_at": asset.created_at.isoformat() if asset.created_at else None,
            "media_id": asset.media_id,
            "media_filename": media.filename if media else None,
            "project_id": asset.project_id,
        })

    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "items": result,
    }


@router.post("/content/{content_id}/rewrite")
def rewrite_content(
    content_id: int,
    data: ContentGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Rewrite a generated content asset with a different tone or instructions."""
    asset = verify_content_ownership(content_id, current_user, db)

    from backend.services.content_generator import ContentGenerator
    generator = ContentGenerator(db)

    try:
        rewritten = generator.rewrite_content(
            original_body=asset.body_json,
            content_type=asset.content_type,
            tone=data.tone,
            extra_instructions=data.extra_instructions,
        )
    except RuntimeError as rt_err:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(rt_err),
        )

    asset.body_json = rewritten
    db.commit()
    db.refresh(asset)
    return GeneratedContentResponse.model_validate(asset)
