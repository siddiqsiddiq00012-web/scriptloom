from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.core.dependencies import get_current_user
from backend.db.dependencies import get_db
from backend.models.user import User
from backend.schemas.voice_dna import VoiceDNAResponse, VoiceDNAUpdate
from backend.services.voice_dna_service import VoiceDNAService

router = APIRouter(
    prefix="/voice-dna",
    tags=["Voice DNA"],
)


@router.get(
    "/me",
    response_model=VoiceDNAResponse,
)
def get_voice_dna(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = VoiceDNAService(db)
    dna = service.get_or_create_profile(current_user.id)
    return VoiceDNAResponse.model_validate(dna)


@router.put(
    "/me",
    response_model=VoiceDNAResponse,
)
def update_voice_dna(
    update_data: VoiceDNAUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = VoiceDNAService(db)
    updated_dna = service.update_profile(current_user.id, update_data)
    return VoiceDNAResponse.model_validate(updated_dna)
