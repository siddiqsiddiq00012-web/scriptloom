import io
import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from botocore.exceptions import ClientError
from fastapi import HTTPException

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.core.config import Settings
from backend.storage.base import validate_storage_key
from backend.storage.local import LocalStorage
from backend.storage.r2 import R2Storage
from backend.services.upload_service import UploadService
from backend.services.media_pipeline import MediaPipeline
from backend.services.processing_service import ProcessingService
from backend.db.database import SessionLocal
from backend.models.user import User
from backend.models.project import Project
from backend.models.media import Media


# 1. CENTRALIZED KEY VALIDATION TESTS
def test_storage_key_validation():
    # Valid canonical keys
    validate_storage_key("projects/1/media/uuid.mp4")
    validate_storage_key("projects/25/clips/clip_uuid.mp4")
    validate_storage_key("projects/999/waveforms/10_waveform.json")

    # Invalid keys (path traversal, absolute, backslashes, drive prefixes)
    with pytest.raises(ValueError, match="cannot be empty"):
        validate_storage_key("")
    with pytest.raises(ValueError, match="Path traversal"):
        validate_storage_key("projects/1/../../etc/passwd")
    with pytest.raises(ValueError, match="Backslashes"):
        validate_storage_key("projects\\1\\media\\file.mp4")
    with pytest.raises(ValueError, match="prefix indicators"):
        validate_storage_key("/absolute/path")
    with pytest.raises(ValueError, match="prefix indicators"):
        validate_storage_key("./relative/path")
    with pytest.raises(ValueError, match="Drive prefixes"):
        validate_storage_key("C:/media/file.mp4")


# 2. LOCAL STORAGE PROVIDER TESTS
def test_local_storage_crud():
    with tempfile.TemporaryDirectory() as tmp_root:
        local_backend = LocalStorage(root_directory=tmp_root)
        key = "projects/1/media/test_file.txt"
        content = b"Local Storage persistent verification bytes"

        # Save Stream
        local_backend.save_stream(key, [content], len(content))

        # Check Existence
        assert local_backend.exists(key) is True

        # Read Stream
        read_chunks = list(local_backend.read_stream(key))
        assert b"".join(read_chunks) == content

        # Materialization yields local path and preserves file on exit
        with local_backend.materialize(key) as local_path:
            assert local_path.exists() is True
            assert local_path.read_bytes() == content
        
        # Ensure path was NOT deleted after local materialize exit
        assert local_backend.exists(key) is True

        # Resolve containment check
        with pytest.raises(ValueError, match="Path traversal"):
            local_backend._resolve_key("projects/1/../../../outside.txt")

        # Delete
        local_backend.delete(key)
        assert local_backend.exists(key) is False


# 3. LEGACY KEY LOCAL COMPATIBILITY & R2 REJECTION
def test_legacy_key_compatibility():
    with tempfile.TemporaryDirectory() as tmp_root:
        local_backend = LocalStorage(root_directory=tmp_root)
        
        # Write a legacy file directly into the workspace root
        legacy_key = "media/uploads/legacy_test_file.wav"
        legacy_path = Path(".") / legacy_key
        legacy_path.parent.mkdir(parents=True, exist_ok=True)
        
        content = b"Legacy wav header content mockup"
        legacy_path.write_bytes(content)

        try:
            # Local Storage must successfully resolve and read the legacy file
            assert local_backend.exists(legacy_key) is True
            read_chunks = list(local_backend.read_stream(legacy_key))
            assert b"".join(read_chunks) == content
        finally:
            # Clean up local workspace legacy file
            if legacy_path.exists():
                os.remove(legacy_path)
                try:
                    os.rmdir(legacy_path.parent)
                except Exception:
                    pass

        # R2 Storage backend must return False / raise Error on legacy paths without network access
        with patch("boto3.client") as mock_boto:
            mock_s3 = MagicMock()
            mock_boto.return_value = mock_s3
            # s3 head_object raises 404 ClientError to simulate missing key
            mock_s3.head_object.side_effect = ClientError({"Error": {"Code": "404", "Message": "Not Found"}}, "HeadObject")
            mock_s3.get_object.side_effect = ClientError({"Error": {"Code": "NoSuchKey", "Message": "Not Found"}}, "GetObject")

            r2_backend = R2Storage("http://dummy", "bucket", "key", "secret")
            assert r2_backend.exists("media/uploads/legacy_test_file.wav") is False
            with pytest.raises(FileNotFoundError):
                list(r2_backend.read_stream("media/uploads/legacy_test_file.wav"))


# 4. MOCKED R2 STORAGE PROVIDER CRUD
@patch("boto3.client")
def test_mocked_r2_storage_crud(mock_boto_client):
    mock_s3 = MagicMock()
    mock_boto_client.return_value = mock_s3

    r2_backend = R2Storage(
        endpoint_url="https://dummy.r2.cloudflare.com",
        bucket_name="scriptloom-bucket",
        access_key_id="test_key_id",
        secret_access_key="test_secret",
    )

    key = "projects/1/media/test_r2_file.mp4"
    content = b"Mocked Cloudflare R2 binary content chunk"

    # Mock get_object body stream
    mock_response = {
        "Body": MagicMock()
    }
    mock_response["Body"].iter_chunks.return_value = [content]
    mock_s3.get_object.return_value = mock_response

    # Save
    r2_backend.save_stream(key, [content], len(content))
    mock_s3.upload_fileobj.assert_called_once()

    # Read
    read_chunks = list(r2_backend.read_stream(key))
    assert b"".join(read_chunks) == content
    mock_s3.get_object.assert_called_once_with(Bucket="scriptloom-bucket", Key=key)

    # Existence Check
    mock_s3.head_object.return_value = {}
    assert r2_backend.exists(key) is True

    # Materialization downloads, yields temp path, and deletes temp file on exit
    with r2_backend.materialize(key) as temp_path:
        assert temp_path.exists() is True
        assert temp_path.read_bytes() == content
        saved_temp_path = temp_path
    
    # Ensure materialized file is deleted on exit
    assert saved_temp_path.exists() is False

    # Delete
    r2_backend.delete(key)
    mock_s3.delete_object.assert_called_with(Bucket="scriptloom-bucket", Key=key)


# 5. CONFIGURATION CONDITIONAL VALIDATION
def test_storage_configuration_validation():
    # 1. Local Mode requires LOCAL_STORAGE_ROOT
    s1 = Settings(
        DATABASE_URL="sqlite://",
        SECRET_KEY="test_secret",
        GEMINI_API_KEY="test_gemini",
        GOOGLE_CLIENT_ID="test_google",
        ALLOWED_ORIGINS="*",
        STORAGE_BACKEND="local",
        LOCAL_STORAGE_ROOT="test_media_folder",
    )
    assert s1.STORAGE_BACKEND == "local"

    # 2. R2 Mode requires all credentials, startup fails if missing
    with pytest.raises(ValueError, match="Missing required R2 credentials"):
        Settings(
            DATABASE_URL="sqlite://",
            SECRET_KEY="test_secret",
            GEMINI_API_KEY="test_gemini",
            GOOGLE_CLIENT_ID="test_google",
            ALLOWED_ORIGINS="*",
            STORAGE_BACKEND="r2",
            R2_ENDPOINT_URL="",  # Missing
        )


# 6. UPLOAD FORMAT VALIDATION & DB FAILURE ROLLBACK
@patch("backend.services.ffprobe_service.FFprobeService.extract_metadata")
@patch("backend.storage.manager.storage.save_stream")
@patch("backend.storage.manager.storage.delete")
def test_upload_format_and_rollback_lifecycles(mock_delete, mock_save, mock_extract):
    db = SessionLocal()
    # Setup test user/project
    user = db.query(User).filter(User.email == "up_test@scriptloom.ai").first()
    if not user:
        user = User(name="Uploader", email="up_test@scriptloom.ai", hashed_password="hashed")
        db.add(user)
        db.commit()
        db.refresh(user)

    project = db.query(Project).filter(Project.owner_id == user.id).first()
    if not project:
        project = Project(name="Upload Project", owner_id=user.id)
        db.add(project)
        db.commit()
        db.refresh(project)

    project_id = project.id
    db.close()

    mock_extract.return_value = MagicMock(duration=10.0, width=1920, height=1080, codec="h264", bitrate=5000, fps=30.0)

    # 1. Invalid upload (FFprobe failure) should clean up/reject before save
    mock_extract.side_effect = Exception("FFprobe metadata format extraction failed")
    
    mock_file = MagicMock()
    mock_file.filename = "corrupted_media.mp4"
    mock_file.content_type = "video/mp4"
    mock_file.file.read.side_effect = [b"broken video stream header", b""]

    service = UploadService(SessionLocal())
    with pytest.raises(HTTPException) as exc:
        import asyncio
        asyncio.run(service.upload(project_id=project_id, file=mock_file))
    
    assert exc.value.status_code == 400
    assert "Invalid media file" in exc.value.detail
    mock_save.assert_not_called()

    # 2. Database Insertion failure after storage saves -> Rollback/delete the uploaded key
    mock_extract.side_effect = None
    mock_extract.return_value = MagicMock(duration=10.0, width=1920, height=1080, codec="h264", bitrate=5000, fps=30.0)
    
    mock_file2 = MagicMock()
    mock_file2.filename = "valid_but_db_fails.mp4"
    mock_file2.content_type = "video/mp4"
    mock_file2.file.read.side_effect = [b"valid video stream metadata content header", b""]

    # We patch create_media to raise an error
    with patch("backend.repositories.media_repository.MediaRepository.create_media", side_effect=Exception("Database connection timed out")):
        with pytest.raises(Exception, match="Database connection timed out"):
            asyncio.run(service.upload(project_id=project_id, file=mock_file2))

        # Persistent storage rollback must trigger delete
        mock_save.assert_called_once()
        mock_delete.assert_called_once()


# 7. PARTIAL GENERATION FAILURE CLEANS STORAGE CLIPS
@patch("backend.processing.pipeline.service.ProcessingPipeline.process_video")
@patch("backend.storage.manager.storage.save_stream")
@patch("backend.storage.manager.storage.delete")
@patch("backend.storage.manager.storage.exists", return_value=True)
@patch("backend.storage.manager.storage.materialize")
def test_partial_processing_failure_removes_orphaned_clips(mock_mat, mock_exists, mock_delete, mock_save, mock_process):
    # Setup materialize context manager mock
    mock_context = MagicMock()
    mock_context.__enter__.return_value = Path(__file__)
    mock_mat.return_value = mock_context

    db = SessionLocal()
    user = db.query(User).filter(User.email == "partial@scriptloom.ai").first()
    if not user:
        user = User(name="Partial User", email="partial@scriptloom.ai", hashed_password="hashed")
        db.add(user)
        db.commit()
        db.refresh(user)

    project = db.query(Project).filter(Project.owner_id == user.id).first()
    if not project:
        project = Project(name="Partial Project", owner_id=user.id)
        db.add(project)
        db.commit()
        db.refresh(project)

    media = db.query(Media).filter(Media.project_id == project.id).first()
    if not media:
        media = Media(project_id=project.id, filename="video.mp4", storage_path=f"projects/{project.id}/media/abc.mp4", file_size=100)
        db.add(media)
        db.commit()
        db.refresh(media)
    
    media_id = media.id
    user_id = user.id
    db.close()

    mock_temp_dir = tempfile.mkdtemp()
    temp_clip_1 = Path(mock_temp_dir) / "clip_1.mp4"
    temp_clip_1.touch()
    temp_clip_2 = Path(mock_temp_dir) / "clip_2.mp4"
    temp_clip_2.touch()
    temp_clip_3 = Path(mock_temp_dir) / "clip_3.mp4"
    temp_clip_3.touch()

    mock_process.return_value = [
        {"title": "Clip 1", "start_time": 0.0, "end_time": 5.0, "reason": "reason 1", "output": str(temp_clip_1)},
        {"title": "Clip 2", "start_time": 5.0, "end_time": 10.0, "reason": "reason 2", "output": str(temp_clip_2)},
        {"title": "Clip 3", "start_time": 10.0, "end_time": 15.0, "reason": "reason 3", "output": str(temp_clip_3)},
    ]

    call_count = 0
    def save_side_effect(key, stream, size):
        nonlocal call_count
        call_count += 1
        if call_count == 3:
            raise RuntimeError("Cloudflare R2 storage write quota exceeded")
        return None

    mock_save.side_effect = save_side_effect

    db_session = SessionLocal()
    service = ProcessingService(db_session)
    try:
        job, video_path, _ = service.create_job(media_id, user_id)
        # Run background processing task (should catch exception and run compensation cleanups)
        try:
            service.process_job(job.job_id, video_path)
        except Exception:
            pass
    finally:
        db_session.close()

    try:
        assert mock_delete.call_count >= 2
        delete_keys = [c[0][0] for c in mock_delete.call_args_list]
        assert any("clips" in k for k in delete_keys)
    finally:
        shutil.rmtree(mock_temp_dir)


# 8. SAFE DELETION ORDERING ENFORCEMENT
def test_safe_deletion_ordering_integrity():
    db = SessionLocal()
    user = db.query(User).filter(User.email == "del_test@scriptloom.ai").first()
    if not user:
        user = User(name="Deleter", email="del_test@scriptloom.ai", hashed_password="hashed")
        db.add(user)
        db.commit()
        db.refresh(user)

    project = db.query(Project).filter(Project.owner_id == user.id).first()
    if not project:
        project = Project(name="Deletion Project", owner_id=user.id)
        db.add(project)
        db.commit()
        db.refresh(project)

    media = Media(project_id=project.id, filename="delete_target.mp4", storage_path=f"projects/{project.id}/media/target.mp4", file_size=500)
    db.add(media)
    db.commit()
    db.refresh(media)

    media_id = media.id
    user_id = user.id
    db.close()

    from backend.core.token import create_access_token
    token = create_access_token({"sub": str(user_id)})
    headers = {"Authorization": f"Bearer {token}"}

    # If storage.delete raises a Server-Side Error -> Database record MUST remain intact!
    from fastapi.testclient import TestClient
    from backend.main import app
    client = TestClient(app)

    # We mock storage.exists to return True and storage.delete to raise Error
    with patch("backend.storage.manager.storage.exists", return_value=True), \
         patch("backend.storage.manager.storage.delete", side_effect=RuntimeError("Cloudflare S3 boundary connection error")):
         
         response = client.delete(f"/projects/media/{media_id}", headers=headers)
         assert response.status_code == 500
         assert "Failed to delete associated storage objects" in response.json()["detail"]

         # Verify database record still exists (no database records were deleted!)
         db = SessionLocal()
         db_media = db.query(Media).filter(Media.id == media_id).first()
         assert db_media is not None
         
         # Clean up test media safely
         db.delete(db_media)
         db.commit()
         db.close()
