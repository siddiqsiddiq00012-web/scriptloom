import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.db.dependencies import get_db
from backend.core.config import settings

router = APIRouter(
    tags=["Health & Readiness"],
)


@router.get("/health")
def get_health():
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "app_version": settings.APP_VERSION,
    }


@router.get("/live")
def get_liveness():
    return {"status": "alive"}


@router.get("/ready")
def get_readiness(db: Session = Depends(get_db)):
    db_ok = False
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    # Check the actual storage root used by the StorageProvider, not MEDIA_FOLDER
    from backend.storage.manager import storage
    storage_ok = False
    if hasattr(storage, "root_directory"):
        storage_ok = str(storage.root_directory).strip() != "" and True
    elif hasattr(storage, "bucket_name"):
        # R2: storage exists by config (validated at startup)
        storage_ok = True

    if not db_ok:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Readiness check failed: Database unreachable.",
        )

    return {
        "status": "ready",
        "database": "connected",
        "storage": "configured" if storage_ok else "unconfigured",
    }