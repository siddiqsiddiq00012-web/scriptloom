from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from backend.core.dependencies import get_current_user, verify_content_ownership, verify_media_ownership
from backend.db.dependencies import get_db
from backend.models.user import User
from backend.services.export_engine import ExportEngine

router = APIRouter(
    prefix="/export",
    tags=["Export Engine"],
)


def _safe_header(filename: str) -> str:
    """Return a Content-Disposition header value safe for latin-1 encoding."""
    safe = filename.encode("ascii", errors="ignore").decode("ascii").strip()
    if not safe:
        safe = "download"
    return f'attachment; filename="{safe}"'


@router.get("/content/{content_id}")
def export_single_asset(
    content_id: int,
    format: str = Query("markdown", description="Format: markdown | txt | json"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Verify content ownership before exporting single asset
    verify_content_ownership(content_id, current_user, db)

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
                "Content-Disposition": _safe_header(filename),
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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Verify media ownership before exporting campaign zip
    verify_media_ownership(media_id, current_user, db)

    engine = ExportEngine(db)
    try:
        filename, zip_bytes, media_type = engine.export_campaign_zip(media_id)
        return Response(
            content=zip_bytes,
            media_type=media_type,
            headers={
                "Content-Disposition": _safe_header(filename),
            },
        )
    except ValueError as val_err:
        raise HTTPException(
            status_code=404,
            detail=str(val_err),
        )
