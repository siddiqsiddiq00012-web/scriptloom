import logging
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.db.dependencies import get_db
from backend.models.media import Media
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
    db: Session = Depends(get_db),
):
    media_repo = MediaRepository(db)
    media = media_repo.get_by_id(media_id)

    if media is None:
        raise HTTPException(
            status_code=404,
            detail="Media not found",
        )

    # Locate extracted audio WAV file
    media_path = Path(media.storage_path)
    audio_wav_path = media_path.parent / f"{media.id}_audio.wav"

    if not audio_wav_path.exists():
        # Fallback to source media path
        audio_wav_path = media_path

    stt_engine = STTEngine()
    
    try:
        stt_result = stt_engine.transcribe(audio_wav_path)
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
    db: Session = Depends(get_db),
):
    transcript_repo = TranscriptRepository(db)
    transcript = transcript_repo.get_by_media_id(media_id)

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
    db: Session = Depends(get_db),
):
    transcript_repo = TranscriptRepository(db)
    updated_segment = transcript_repo.update_segment(
        segment_id=segment_id,
        speaker_label=update_data.speaker_label,
        text=update_data.text,
        chapter_title=update_data.chapter_title,
    )

    if updated_segment is None:
        raise HTTPException(
            status_code=404,
            detail="Transcript segment not found",
        )

    return TranscriptSegmentResponse.model_validate(updated_segment)
