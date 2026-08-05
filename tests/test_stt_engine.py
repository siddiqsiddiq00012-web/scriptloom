import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import status
from fastapi.testclient import TestClient
from backend.main import app
from backend.db.database import SessionLocal
from backend.models.user import User
from backend.models.project import Project
from backend.models.media import Media
from backend.models.transcript import Transcript, TranscriptSegment
from backend.processing.stt_engine import (
    STTEngine,
    STTConfigurationError,
    STTTranscriptionError,
)
from backend.processing.pipeline.service import ProcessingPipeline

client = TestClient(app)


# Mock Segment for faster_whisper mock output
class MockSegment:
    def __init__(self, start, end, text):
        self.start = start
        self.end = end
        self.text = text


class MockInfo:
    def __init__(self, language="en", duration=60.0):
        self.language = language
        self.duration = duration


# 1. Success with Mocked external Whisper dependency
@patch("faster_whisper.WhisperModel")
def test_stt_engine_success(mock_whisper_class):
    mock_model = MagicMock()
    mock_whisper_class.return_value = mock_model

    # Setup mocked transcribe results
    mock_segments = [
        MockSegment(0.0, 10.0, "Hello world"),
        MockSegment(10.0, 20.0, "Welcome to the podcast"),
    ]
    mock_info = MockInfo(language="en", duration=20.0)
    mock_model.transcribe.return_value = (mock_segments, mock_info)

    engine = STTEngine()
    result = engine.transcribe(__file__)  # Use any existing file path

    assert result["language"] == "en"
    assert result["duration"] == 20.0
    assert len(result["segments"]) == 2
    assert result["segments"][0]["text"] == "Hello world"
    assert result["segments"][1]["text"] == "Welcome to the podcast"


# 2. Model/provider loading failure
@patch("faster_whisper.WhisperModel", side_effect=ImportError("faster_whisper libraries missing"))
def test_stt_engine_loading_failure(mock_whisper_class):
    engine = STTEngine()
    with pytest.raises(STTConfigurationError) as exc_info:
        engine.transcribe(__file__)
    
    assert "Failed to load Whisper model" in str(exc_info.value)
    assert exc_info.value.__cause__ is not None  # Verify exception chaining


# 3. Transcription execution failure
@patch("faster_whisper.WhisperModel")
def test_stt_engine_transcription_failure(mock_whisper_class):
    mock_model = MagicMock()
    mock_whisper_class.return_value = mock_model
    mock_model.transcribe.side_effect = RuntimeError("GPU out of memory")

    engine = STTEngine()
    with pytest.raises(STTTranscriptionError) as exc_info:
        engine.transcribe(__file__)
        
    assert "Whisper transcription failed" in str(exc_info.value)
    assert exc_info.value.__cause__ is not None  # Verify exception chaining


# 4. Empty/no-speech transcription
@patch("faster_whisper.WhisperModel")
def test_stt_engine_empty_transcription(mock_whisper_class):
    mock_model = MagicMock()
    mock_whisper_class.return_value = mock_model
    mock_model.transcribe.return_value = ([], MockInfo(duration=0.0))  # Empty list of segments

    engine = STTEngine()
    with pytest.raises(STTTranscriptionError) as exc_info:
        engine.transcribe(__file__)
        
    assert "No speech detected or transcription is empty" in str(exc_info.value)


# 5. Failed API transcription creates no database records
@patch("backend.processing.stt_engine.STTEngine.transcribe", side_effect=STTTranscriptionError("Failed STT"))
def test_api_transcription_failure_db_state(mock_transcribe):
    db = SessionLocal()
    # Setup user and project
    user = db.query(User).filter(User.email == "db_test@scriptloom.ai").first()
    if not user:
        user = User(name="DB Tester", email="db_test@scriptloom.ai", hashed_password="hashed")
        db.add(user)
        db.commit()
        db.refresh(user)

    project = db.query(Project).filter(Project.owner_id == user.id).first()
    if not project:
        project = Project(name="DB Project", owner_id=user.id)
        db.add(project)
        db.commit()
        db.refresh(project)

    # Setup media with non-nullable file_size
    media = Media(project_id=project.id, filename="test_audio.wav", storage_path=__file__, file_size=1024)
    db.add(media)
    db.commit()
    db.refresh(media)

    media_id = media.id
    user_id = user.id
    db.close()

    from backend.core.token import create_access_token
    token = create_access_token({"sub": str(user_id)})
    headers = {"Authorization": f"Bearer {token}"}

    # Call API which triggers mock failure
    response = client.post(f"/media/{media_id}/transcribe", headers=headers)
    assert response.status_code == 422
    assert response.json()["detail"] == "Failed to transcribe media: No speech detected or invalid audio."

    # Verify no database records were created for Transcript or TranscriptSegment
    db = SessionLocal()
    db_transcript = db.query(Transcript).filter(Transcript.media_id == media_id).first()
    assert db_transcript is None

    # Clean up test media
    db.delete(media)
    db.commit()
    db.close()


# 6. Downstream clip processing guard fails on empty transcript
@patch("backend.processing.transcription.service.WhisperService.transcribe")
def test_pipeline_downstream_guard_on_empty_transcription(mock_transcribe_service):
    # Setup mock to return empty segments
    mock_transcribe_service.return_value = {
        "language": "en",
        "duration": 0.0,
        "segments": []
    }

    pipeline = ProcessingPipeline()
    # Mock other services to verify they are NEVER called if transcription fails/is empty
    pipeline.gemini = MagicMock()
    pipeline.extractor = MagicMock()

    with pytest.raises(RuntimeError) as exc_info:
        pipeline.process_video("dummy_path.mp4", "output_dir")

    assert "No transcript segments found to generate clips from." in str(exc_info.value)
    
    # Verify downstream services were never called
    pipeline.gemini.analyze_transcript.assert_not_called()
    pipeline.extractor.extract_clip.assert_not_called()
