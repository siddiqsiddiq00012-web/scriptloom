from fastapi import APIRouter

from backend.api.auth import router as auth_router
from backend.api.clips import router as clips_router
from backend.api.health import router as health_router
from backend.api.processing import router as processing_router
from backend.api.projects import router as projects_router
from backend.api.root import router as root_router
from backend.api.transcripts import router as transcripts_router
from backend.api.uploads import router as uploads_router
from backend.api.users import router as users_router

api_router = APIRouter()

api_router.include_router(root_router)
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(projects_router)
api_router.include_router(uploads_router)
api_router.include_router(transcripts_router)
api_router.include_router(processing_router)
api_router.include_router(clips_router)