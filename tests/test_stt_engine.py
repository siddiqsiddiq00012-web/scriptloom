import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch, call
import pytest
from botocore.exceptions import ClientError
from fastapi import status
from fastapi.testclient import TestClient

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

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
from backend.storage.local import LocalStorage
from backend.storage.r2 import R2Storage

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


# 1. STT Engine Direct Unit Tests
@patch("faster_whisper.WhisperModel")
def test_stt_engine_success(mock_whisper_class):
    mock_model = MagicMock()
    mock_whisper_class.return_value = mock_model

    mock_segments = [
        MockSegment(0.0, 10.0, "Hello world"),
        MockSegment(10.0, 20.0, "Welcome to the podcast"),
    ]
    mock_info = MockInfo(language="en", duration=20.0)
    mock_model.transcribe.return_value = (mock_segments, mock_info)

    engine = STTEngine()
    result = engine.transcribe(__file__)

    assert result["language"] == "en"
    assert result["duration"] == 20.0
    assert len(result["segments"]) == 2
    assert result["segments"][0]["text"] == "Hello world"


@patch("faster_whisper.WhisperModel", side_effect=ImportError("faster_whisper libraries missing"))
def test_stt_engine_loading_failure(mock_whisper_class):
    engine = STTEngine()
    with pytest.raises(STTConfigurationError) as exc_info:
        engine.transcribe(__file__)
    assert "Failed to load Whisper model" in str(exc_info.value)


@patch("faster_whisper.WhisperModel")
def test_stt_engine_transcription_failure(mock_whisper_class):
    mock_model = MagicMock()
    mock_whisper_class.return_value = mock_model
    mock_model.transcribe.side_effect = RuntimeError("GPU out of memory")

    engine = STTEngine()
    with pytest.raises(STTTranscriptionError) as exc_info:
        engine.transcribe(__file__)
    assert "Whisper transcription failed" in str(exc_info.value)


@patch("faster_whisper.WhisperModel")
def test_stt_engine_empty_transcription(mock_whisper_class):
    mock_model = MagicMock()
    mock_whisper_class.return_value = mock_model
    mock_model.transcribe.return_value = ([], MockInfo(duration=0.0))

    engine = STTEngine()
    with pytest.raises(STTTranscriptionError) as exc_info:
        engine.transcribe(__file__)
    assert "No speech detected or transcription is empty" in str(exc_info.value)


# 2. LocalStorage Materialization and API Integration Tests
def test_api_local_storage_transcription_success():
    db = SessionLocal()
    user = db.query(User).filter(User.email == "local_stt@scriptloom.ai").first()
    if not user:
        user = User(name="Local User", email="local_stt@scriptloom.ai", hashed_password="hashed")
        db.add(user)
        db.commit()
        db.refresh(user)

    project = db.query(Project).filter(Project.owner_id == user.id).first()
    if not project:
        project = Project(name="Local Project", owner_id=user.id)
        db.add(project)
        db.commit()
        db.refresh(project)

    # Use a valid canonical storage path relative to LOCAL_STORAGE_ROOT
    from backend.core.config import settings
    storage_dir = Path(settings.LOCAL_STORAGE_ROOT)
    storage_dir.mkdir(exist_ok=True)
    
    canonical_key = "projects/1/media/test_local_video.mp4"
    disk_path = storage_dir / canonical_key
    disk_path.parent.mkdir(parents=True, exist_ok=True)
    disk_path.write_bytes(b"dummy video data")

    media = Media(
        project_id=project.id,
        filename="test_local_video.mp4",
        storage_path=canonical_key,
        file_size=len(b"dummy video data"),
        status="uploaded"
    )
    db.add(media)
    db.commit()
    db.refresh(media)

    media_id = media.id
    user_id = user.id
    db.close()

    from backend.core.token import create_access_token
    token = create_access_token({"sub": str(user_id)})
    headers = {"Authorization": f"Bearer {token}"}

    # Mock STTEngine.transcribe to return a successful transcript
    mock_result = {
        "language": "en",
        "duration": 5.0,
        "full_text": "Transcribed hello world content",
        "segments": [{
            "speaker_label": "Speaker 1 (Founder)",
            "start_time": 0.0,
            "end_time": 5.0,
            "text": "Transcribed hello world content",
            "chapter_title": "Chapter 1",
            "key_assertion": "Key claim"
        }]
    }

    with patch("backend.processing.stt_engine.STTEngine.transcribe", return_value=mock_result) as mock_stt:
        response = client.post(f"/api/v1/media/{media_id}/transcribe", headers=headers)
        assert response.status_code == 201
        
        # Verify STTEngine received materialized path (which is the actual disk path)
        called_path = mock_stt.call_args[0][0]
        assert isinstance(called_path, Path)
        assert called_path.name == "test_local_video.mp4"
        assert called_path.exists() is True

        # Verify DB records
        db = SessionLocal()
        db_transcript = db.query(Transcript).filter(Transcript.media_id == media_id).first()
        assert db_transcript is not None
        assert db_transcript.language == "en"
        assert len(db_transcript.segments) == 1

        # Clean up database
        db_media = db.query(Media).filter(Media.id == media_id).first()
        if db_media:
            db.delete(db_media)
        db_trans = db.query(Transcript).filter(Transcript.media_id == media_id).first()
        if db_trans:
            db.delete(db_trans)
        db.commit()
        db.close()

    # Clean local disk file
    if disk_path.exists():
        os.remove(disk_path)


# 3. Mocked R2 Materialization and Deletion Guarantees
@patch("boto3.client")
def test_api_r2_storage_transcription_success(mock_boto_client):
    # Setup R2Storage mocks
    mock_s3 = MagicMock()
    mock_boto_client.return_value = mock_s3
    mock_response = {
        "Body": MagicMock()
    }
    mock_response["Body"].iter_chunks.return_value = [b"r2 video chunk bytes"]
    mock_s3.get_object.return_value = mock_response
    mock_s3.head_object.return_value = {}

    db = SessionLocal()
    user = db.query(User).filter(User.email == "r2_stt@scriptloom.ai").first()
    if not user:
        user = User(name="R2 User", email="r2_stt@scriptloom.ai", hashed_password="hashed")
        db.add(user)
        db.commit()
        db.refresh(user)

    project = db.query(Project).filter(Project.owner_id == user.id).first()
    if not project:
        project = Project(name="R2 Project", owner_id=user.id)
        db.add(project)
        db.commit()
        db.refresh(project)

    media = Media(
        project_id=project.id,
        filename="r2_video.mp4",
        storage_path="projects/1/media/r2_video.mp4",
        file_size=20,
        status="uploaded"
    )
    db.add(media)
    db.commit()
    db.refresh(media)

    media_id = media.id
    user_id = user.id
    db.close()

    # Switch config to R2 storage temporarily by modifying manager storage attribute
    import backend.storage.manager
    original_storage = backend.storage.manager.storage
    r2_backend = R2Storage("https://dummy.r2.com", "bucket", "key", "secret")
    backend.storage.manager.storage = r2_backend

    from backend.core.token import create_access_token
    token = create_access_token({"sub": str(user_id)})
    headers = {"Authorization": f"Bearer {token}"}

    mock_result = {
        "language": "en",
        "duration": 10.0,
        "full_text": "R2 audio text content",
        "segments": []
    }

    saved_temp_path = None
    original_transcribe = STTEngine.transcribe

    def transcribe_capture(self, audio_wav_path):
        nonlocal saved_temp_path
        saved_temp_path = Path(audio_wav_path)
        # Verify the file is materialized and exists locally
        assert saved_temp_path.exists() is True
        assert saved_temp_path.read_bytes() == b"r2 video chunk bytes"
        return mock_result

    try:
        with patch.object(STTEngine, "transcribe", transcribe_capture):
            response = client.post(f"/api/v1/media/{media_id}/transcribe", headers=headers)
            assert response.status_code == 201

        # Verify that R2 temporary materialized file was cleaned up/deleted
        assert saved_temp_path is not None
        assert saved_temp_path.exists() is False

    finally:
        backend.storage.manager.storage = original_storage
        db = SessionLocal()
        db_media = db.query(Media).filter(Media.id == media_id).first()
        if db_media:
            db.delete(db_media)
        db_trans = db.query(Transcript).filter(Transcript.media_id == media_id).first()
        if db_trans:
            db.delete(db_trans)
        db.commit()
        db.close()


# 4. R2 Materialization Cleanup on Exception
@patch("boto3.client")
def test_api_r2_storage_materialization_cleanup_on_failure(mock_boto_client):
    mock_s3 = MagicMock()
    mock_boto_client.return_value = mock_s3
    mock_response = {
        "Body": MagicMock()
    }
    mock_response["Body"].iter_chunks.return_value = [b"failure video bytes"]
    mock_s3.get_object.return_value = mock_response
    mock_s3.head_object.return_value = {}

    db = SessionLocal()
    user = db.query(User).filter(User.email == "r2_err@scriptloom.ai").first()
    if not user:
        user = User(name="R2 Error User", email="r2_err@scriptloom.ai", hashed_password="hashed")
        db.add(user)
        db.commit()
        db.refresh(user)

    project = db.query(Project).filter(Project.owner_id == user.id).first()
    if not project:
        project = Project(name="R2 Err Project", owner_id=user.id)
        db.add(project)
        db.commit()
        db.refresh(project)

    media = Media(
        project_id=project.id,
        filename="r2_fail.mp4",
        storage_path="projects/1/media/r2_fail.mp4",
        file_size=20,
        status="uploaded"
    )
    db.add(media)
    db.commit()
    db.refresh(media)

    media_id = media.id
    user_id = user.id
    db.close()

    # Switch config to R2 storage temporarily by modifying manager storage attribute
    import backend.storage.manager
    original_storage = backend.storage.manager.storage
    r2_backend = R2Storage("https://dummy.r2.com", "bucket", "key", "secret")
    backend.storage.manager.storage = r2_backend

    from backend.core.token import create_access_token
    token = create_access_token({"sub": str(user_id)})
    headers = {"Authorization": f"Bearer {token}"}

    saved_temp_path = None
    def transcribe_raise(self, audio_wav_path):
        nonlocal saved_temp_path
        saved_temp_path = Path(audio_wav_path)
        assert saved_temp_path.exists() is True
        raise STTTranscriptionError("Failed mid-transcription")

    try:
        with patch.object(STTEngine, "transcribe", transcribe_raise):
            response = client.post(f"/api/v1/media/{media_id}/transcribe", headers=headers)
            assert response.status_code == 422

        # Verify R2 temporary file was cleaned up even after the exception
        assert saved_temp_path is not None
        assert saved_temp_path.exists() is False

    finally:
        backend.storage.manager.storage = original_storage
        db = SessionLocal()
        db_media = db.query(Media).filter(Media.id == media_id).first()
        if db_media:
            db.delete(db_media)
        db_trans = db.query(Transcript).filter(Transcript.media_id == media_id).first()
        if db_trans:
            db.delete(db_trans)
        db.commit()
        db.close()


# 5. Unauthorized User Check Precedes Materialization
@patch("backend.storage.manager.storage.materialize")
def test_unauthorized_user_blocked_before_materialize(mock_mat):
    db = SessionLocal()
    user_a = db.query(User).filter(User.email == "usera@scriptloom.ai").first()
    if not user_a:
        user_a = User(name="User A", email="usera@scriptloom.ai", hashed_password="hashed")
        db.add(user_a)
        db.commit()
        db.refresh(user_a)

    user_b = db.query(User).filter(User.email == "userb@scriptloom.ai").first()
    if not user_b:
        user_b = User(name="User B", email="userb@scriptloom.ai", hashed_password="hashed")
        db.add(user_b)
        db.commit()
        db.refresh(user_b)

    project = db.query(Project).filter(Project.owner_id == user_a.id).first()
    if not project:
        project = Project(name="Project A", owner_id=user_a.id)
        db.add(project)
        db.commit()
        db.refresh(project)

    media = Media(
        project_id=project.id,
        filename="private_video.mp4",
        storage_path="projects/1/media/private.mp4",
        file_size=20,
        status="uploaded"
    )
    db.add(media)
    db.commit()
    db.refresh(media)

    media_id = media.id
    user_b_id = user_b.id
    db.close()

    from backend.core.token import create_access_token
    # User B (unauthorized) tries to access User A's media
    token = create_access_token({"sub": str(user_b_id)})
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(f"/api/v1/media/{media_id}/transcribe", headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Media not found."

    # Verify that storage.materialize was never invoked
    mock_mat.assert_not_called()

    # Database cleanup
    db = SessionLocal()
    db_media = db.query(Media).filter(Media.id == media_id).first()
    db.delete(db_media)
    db.commit()
    db.close()


# 6. Missing Storage Object Produces 404
def test_missing_storage_object_produces_404():
    db = SessionLocal()
    user = db.query(User).filter(User.email == "missing_file@scriptloom.ai").first()
    if not user:
        user = User(name="Missing File User", email="missing_file@scriptloom.ai", hashed_password="hashed")
        db.add(user)
        db.commit()
        db.refresh(user)

    project = db.query(Project).filter(Project.owner_id == user.id).first()
    if not project:
        project = Project(name="Missing File Project", owner_id=user.id)
        db.add(project)
        db.commit()
        db.refresh(project)

    # Use a non-existent storage key path
    media = Media(
        project_id=project.id,
        filename="nonexistent.mp4",
        storage_path="projects/1/media/nonexistent.mp4",
        file_size=20,
        status="uploaded"
    )
    db.add(media)
    db.commit()
    db.refresh(media)

    media_id = media.id
    user_id = user.id
    db.close()

    from backend.core.token import create_access_token
    token = create_access_token({"sub": str(user_id)})
    headers = {"Authorization": f"Bearer {token}"}

    # API request
    response = client.post(f"/api/v1/media/{media_id}/transcribe", headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Media file not found in storage."

    # Clean up database
    db = SessionLocal()
    db_media = db.query(Media).filter(Media.id == media_id).first()
    db.delete(db_media)
    db.commit()
    db.close()


# 7. Failed API transcription creates no database records
@patch("backend.processing.stt_engine.STTEngine.transcribe", side_effect=STTTranscriptionError("Failed STT"))
@patch("backend.storage.manager.storage.exists", return_value=True)
@patch("backend.storage.manager.storage.materialize")
def test_api_transcription_failure_db_state(mock_mat, mock_exists, mock_transcribe):
    # Setup materialize context manager mock
    mock_context = MagicMock()
    mock_context.__enter__.return_value = Path(__file__)
    mock_mat.return_value = mock_context

    db = SessionLocal()
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

    media = Media(project_id=project.id, filename="test_audio.wav", storage_path="projects/1/media/test_audio.wav", file_size=1024)
    db.add(media)
    db.commit()
    db.refresh(media)

    media_id = media.id
    user_id = user.id
    db.close()

    from backend.core.token import create_access_token
    token = create_access_token({"sub": str(user_id)})
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(f"/api/v1/media/{media_id}/transcribe", headers=headers)
    assert response.status_code == 422
    assert response.json()["detail"] == "Failed to transcribe media: No speech detected or invalid audio."

    db = SessionLocal()
    db_transcript = db.query(Transcript).filter(Transcript.media_id == media_id).first()
    assert db_transcript is None

    db_media = db.query(Media).filter(Media.id == media_id).first()
    if db_media:
        db.delete(db_media)
    db_trans = db.query(Transcript).filter(Transcript.media_id == media_id).first()
    if db_trans:
        db.delete(db_trans)
    db.commit()
    db.close()


# 8. Downstream clip processing guard fails on empty transcript
@patch("backend.processing.transcription.service.WhisperService.transcribe")
def test_pipeline_downstream_guard_on_empty_transcription(mock_transcribe_service):
    mock_transcribe_service.return_value = {
        "language": "en",
        "duration": 0.0,
        "segments": []
    }

    pipeline = ProcessingPipeline()
    pipeline.gemini = MagicMock()
    pipeline.extractor = MagicMock()

    with pytest.raises(RuntimeError) as exc_info:
        pipeline.process_video("dummy_path.mp4", "output_dir")

    assert "No transcript segments found to generate clips from." in str(exc_info.value)
    pipeline.gemini.analyze_transcript.assert_not_called()
    pipeline.extractor.extract_clip.assert_not_called()
