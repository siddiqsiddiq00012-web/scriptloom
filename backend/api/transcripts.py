import logging
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.db.dependencies import get_db
from backend.models.user import User
from backend.core.dependencies import (
    get_current_user,
    verify_media_ownership,
    verify_segment_ownership,
)
from backend.processing.stt_engine import STTEngine, STTConfigurationError, STTTranscriptionError
from backend.repositories.media_repository import MediaRepository
from backend.repositories.transcript_repository import TranscriptRepository
from backend.schemas.transcript import (
    SegmentUpdate,
    TranscriptResponse,
    TranscriptSegmentResponse,
)

router = APIRouter(
    tags=["Transcripts"],
)


@router.post(
    "/media/{media_id}/transcribe",
    response_model=TranscriptResponse,
    status_code=status.HTTP_201_CREATED,
)
def transcribe_media(
    media_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Verify media ownership before starting transcription
    media = verify_media_ownership(media_id, current_user, db)

    # Locate and materialize the media file from storage
    from backend.storage.manager import storage
    if not storage.exists(media.storage_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media file not found in storage."
        )

    stt_engine = STTEngine()
    
    try:
        with storage.materialize(media.storage_path) as local_media_path:
            stt_result = stt_engine.transcribe(local_media_path)
    except STTConfigurationError as e:
        logging.error(f"[STTEngine Config Error] {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Transcription provider is misconfigured or unavailable."
        )
    except STTTranscriptionError as e:
        logging.error(f"[STTEngine Transcription Error] {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Failed to transcribe media: No speech detected or invalid audio."
        )
    except HTTPException as he:
        # Re-raise standard FastAPI HTTPExceptions
        raise he
    except Exception as e:
        logging.error(f"[STTEngine Unexpected Error] {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during transcription."
        )

    transcript_repo = TranscriptRepository(db)
    transcript = transcript_repo.create_transcript(
        media_id=media.id,
        language=stt_result.get("language", "en"),
        full_text=stt_result.get("full_text", ""),
        summary=stt_result.get("summary"),
    )

    transcript_repo.add_segments(
        transcript_id=transcript.id,
        segments_data=stt_result.get("segments", []),
    )

    full_transcript = transcript_repo.get_by_media_id(media.id)
    return TranscriptResponse.model_validate(full_transcript)


@router.get(
    "/media/{media_id}/transcript",
    response_model=TranscriptResponse,
)
def get_media_transcript(
    media_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Verify media ownership before retrieving transcript
    media = verify_media_ownership(media_id, current_user, db)

    transcript_repo = TranscriptRepository(db)
    transcript = transcript_repo.get_by_media_id(media.id)

    if transcript is None:
        raise HTTPException(
            status_code=404,
            detail="Transcript not found for this media. Call /media/{media_id}/transcribe first.",
        )

    return TranscriptResponse.model_validate(transcript)


@router.put(
    "/transcripts/segments/{segment_id}",
    response_model=TranscriptSegmentResponse,
)
def update_transcript_segment(
    segment_id: int,
    update_data: SegmentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Verify segment ownership before editing, returning the authorized object directly
    segment = verify_segment_ownership(segment_id, current_user, db)

    transcript_repo = TranscriptRepository(db)
    updated_segment = transcript_repo.update_segment(
        segment=segment,
        speaker_label=update_data.speaker_label,
        text=update_data.text,
        chapter_title=update_data.chapter_title,
    )

    return TranscriptSegmentResponse.model_validate(updated_segment)
