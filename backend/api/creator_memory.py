from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.core.dependencies import get_current_user
from backend.db.dependencies import get_db
from backend.models.user import User
from backend.schemas.creator_memory import (
    MemoryIndexResponse,
    MemoryItemResponse,
    MemorySearchRequest,
)
from backend.services.creator_memory_service import CreatorMemoryService

router = APIRouter(
    prefix="/creator-memory",
    tags=["Creator Memory"],
)


@router.post(
    "/index/{media_id}",
    response_model=MemoryIndexResponse,
    status_code=status.HTTP_201_CREATED,
)
def index_media_memory(
    media_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = CreatorMemoryService(db)
    count = service.index_media_transcript(user_id=current_user.id, media_id=media_id)

    if count == 0:
        raise HTTPException(
            status_code=400,
            detail="No valid transcript segments found for indexing. Ensure media is transcribed first.",
        )

    return MemoryIndexResponse(
        message=f"Indexed {count} spoken quotes & assertions into Creator Memory vector store.",
        indexed_count=count,
        media_id=media_id,
    )


@router.post(
    "/search",
    response_model=list[MemoryItemResponse],
)
def search_creator_memory(
    request: MemorySearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = CreatorMemoryService(db)
    results = service.search_memory(
        user_id=current_user.id,
        query=request.query,
        category=request.category,
        top_k=request.top_k,
    )
    return [MemoryItemResponse.model_validate(item) for item in results]
