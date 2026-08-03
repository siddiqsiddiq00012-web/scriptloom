from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.db.dependencies import get_db
from backend.models.generated_content import GeneratedContent
from backend.schemas.generation import (
    CampaignPackResponse,
    ContentUpdate,
    GeneratedContentResponse,
)
from backend.services.generation_engine import GenerationEngine

router = APIRouter(
    prefix="/generation",
    tags=["AI Generation"],
)


@router.post(
    "/campaign-pack/{media_id}",
    response_model=CampaignPackResponse,
    status_code=status.HTTP_201_CREATED,
)
def generate_campaign_pack(
    media_id: int,
    db: Session = Depends(get_db),
):
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
    db: Session = Depends(get_db),
):
    assets = (
        db.query(GeneratedContent)
        .filter(GeneratedContent.media_id == media_id)
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
    db: Session = Depends(get_db),
):
    asset = (
        db.query(GeneratedContent)
        .filter(GeneratedContent.id == content_id)
        .first()
    )

    if not asset:
        raise HTTPException(
            status_code=404,
            detail="Generated content asset not found",
        )

    if update_data.title is not None:
        asset.title = update_data.title
    if update_data.body_json is not None:
        asset.body_json = update_data.body_json

    db.commit()
    db.refresh(asset)
    return GeneratedContentResponse.model_validate(asset)
