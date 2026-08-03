import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.db.dependencies import get_db
from backend.services.cache_service import cache_service
from backend.core.async_worker import async_worker_pool
from backend.services.performance_monitor import performance_monitor
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
    except Exception as exc:
        db_ok = False

    storage_ok = os.path.exists(settings.MEDIA_FOLDER) or os.makedirs(settings.MEDIA_FOLDER, exist_ok=True) is None

    cache_stats = cache_service.get_stats()
    performance_summary = performance_monitor.get_summary()

    if not db_ok:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Readiness check failed: Database unreachable.",
        )

    return {
        "status": "ready",
        "database": "connected" if db_ok else "unreachable",
        "storage": "writable" if storage_ok else "unwritable",
        "active_worker_tasks": async_worker_pool.active_tasks,
        "cache_stats": cache_stats,
        "performance_metrics": performance_summary,
    }