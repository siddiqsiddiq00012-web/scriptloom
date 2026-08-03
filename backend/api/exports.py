from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from backend.db.dependencies import get_db
from backend.services.export_engine import ExportEngine

router = APIRouter(
    prefix="/export",
    tags=["Export Engine"],
)


@router.get("/content/{content_id}")
def export_single_asset(
    content_id: int,
    format: str = Query("markdown", description="Format: markdown | txt | json"),
    db: Session = Depends(get_db),
):
    engine = ExportEngine(db)
    try:
        filename, content_bytes, media_type = engine.export_single_content(
            content_id=content_id,
            format_type=format,
        )
        return Response(
            content=content_bytes,
            media_type=media_type,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
            },
        )
    except ValueError as val_err:
        raise HTTPException(
            status_code=404,
            detail=str(val_err),
        )


@router.get("/campaign-pack/{media_id}")
def export_campaign_zip(
    media_id: int,
    db: Session = Depends(get_db),
):
    engine = ExportEngine(db)
    try:
        filename, zip_bytes, media_type = engine.export_campaign_zip(media_id)
        return Response(
            content=zip_bytes,
            media_type=media_type,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
            },
        )
    except ValueError as val_err:
        raise HTTPException(
            status_code=404,
            detail=str(val_err),
        )
