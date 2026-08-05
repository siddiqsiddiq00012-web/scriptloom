import os
import sys
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from sqlalchemy.exc import IntegrityError
from fastapi import status
from fastapi.testclient import TestClient

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.main import app
from backend.db.database import SessionLocal, engine
from backend.models.user import User
from backend.models.project import Project
from backend.models.media import Media
from backend.models.processing_job import ProcessingJob, JobStatus
from backend.processing.jobs.manager import job_manager
from backend.core.token import create_access_token
from backend.jobs.tasks.video_processing import process_video as process_video_task
from backend.storage.local import LocalStorage
from backend.storage.r2 import R2Storage

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_db():
    """Ensure database is clean before and after each test."""
    db = SessionLocal()
    # Delete test processing jobs
    db.query(ProcessingJob).delete()
    # Delete test media/projects/users
    db.query(Media).delete()
    db.query(Project).delete()
    db.query(User).filter(User.email.like("%@scriptloom.ai")).delete()
    db.commit()
    db.close()
    yield


def create_test_user_project_media(db, prefix="test"):
    user = User(name=f"{prefix} User", email=f"{prefix}@scriptloom.ai", hashed_password="hashed")
    db.add(user)
    db.commit()
    db.refresh(user)

    project = Project(name=f"{prefix} Project", owner_id=user.id)
    db.add(project)
    db.commit()
    db.refresh(project)

    media = Media(
        project_id=project.id,
        filename=f"{prefix}_video.mp4",
        storage_path=f"projects/{project.id}/media/{prefix}_video.mp4",
        file_size=100,
        status="uploaded"
    )
    db.add(media)
    db.commit()
    db.refresh(media)

    return user, project, media


# 1. PERSISTENCE TESTS
def test_processing_job_persistence():
    db = SessionLocal()
    user, project, media = create_test_user_project_media(db, "persist")
    
    # Create job
    job = job_manager.create_job(db, media_id=media.id, user_id=user.id)
    assert job.job_id is not None
    assert job.status == JobStatus.PENDING
    assert job.media_id == media.id
    assert job.user_id == user.id

    # Verify query in a fresh database session
    db.close()
    db2 = SessionLocal()
    fetched_job = job_manager.get_job(db2, job.job_id)
    assert fetched_job is not None
    assert fetched_job.status == JobStatus.PENDING
    assert fetched_job.media_id == media.id
    db2.close()


# 2. DUPLICATE JOB PREVENTION
def test_duplicate_active_job_prevention():
    db = SessionLocal()
    user, project, media = create_test_user_project_media(db, "dup")

    # Create first active job (PENDING)
    job1 = job_manager.create_job(db, media_id=media.id, user_id=user.id)
    assert job1 is not None

    # Attempt to create second active job (should fail unique index constraint)
    with pytest.raises(IntegrityError):
        # We need a new session transaction block or flush to trigger the constraint
        db2 = SessionLocal()
        try:
            job_manager.create_job(db2, media_id=media.id, user_id=user.id)
        finally:
            db2.close()


def test_api_duplicate_job_returns_409():
    db = SessionLocal()
    user, project, media = create_test_user_project_media(db, "api_dup")
    user_id = user.id
    media_id = media.id
    db.close()

    token = create_access_token({"sub": str(user_id)})
    headers = {"Authorization": f"Bearer {token}"}

    # First request: starts job
    with patch("backend.jobs.tasks.video_processing.process_video.delay") as mock_delay:
        resp1 = client.post("/processing/process", json={"media_id": media_id}, headers=headers)
        assert resp1.status_code == 200
        mock_delay.assert_called_once()

    # Second request: active job running -> returns 409 Conflict
    resp2 = client.post("/processing/process", json={"media_id": media_id}, headers=headers)
    assert resp2.status_code == 409
    assert "An active processing job is already running" in resp2.json()["detail"]


# 3. AUTHORIZATION TESTS
def test_job_authorization_checks():
    db = SessionLocal()
    user_a, project_a, media_a = create_test_user_project_media(db, "usera")
    user_b, project_b, media_b = create_test_user_project_media(db, "userb")
    
    # Create job for User A
    job_a = job_manager.create_job(db, media_id=media_a.id, user_id=user_a.id)
    user_a_id = user_a.id
    user_b_id = user_b.id
    job_a_id = job_a.job_id
    db.close()

    token_a = create_access_token({"sub": str(user_a_id)})
    token_b = create_access_token({"sub": str(user_b_id)})

    # User A queries their own job -> Success
    resp_a = client.get(f"/processing/jobs/{job_a_id}", headers={"Authorization": f"Bearer {token_a}"})
    assert resp_a.status_code == 200
    assert resp_a.json()["status"] == "pending"

    # User B queries User A's job -> 404 (sanitized resource boundary protection)
    resp_b = client.get(f"/processing/jobs/{job_a_id}", headers={"Authorization": f"Bearer {token_b}"})
    assert resp_b.status_code == 404
    assert resp_b.json()["detail"] == "Job not found."

    # Anonymous user -> 401 Unauthorized
    resp_anon = client.get(f"/processing/jobs/{job_a_id}")
    assert resp_anon.status_code == 401


# 4. DISPATCH FAILURE COMPENSATION
@patch("backend.jobs.tasks.video_processing.process_video.delay", side_effect=Exception("Redis connection refused"))
def test_api_dispatch_failure_compensation(mock_delay):
    db = SessionLocal()
    user, project, media = create_test_user_project_media(db, "disp_fail")
    user_id = user.id
    media_id = media.id
    db.close()

    token = create_access_token({"sub": str(user_id)})
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post("/processing/process", json={"media_id": media_id}, headers=headers)
    assert resp.status_code == 500
    assert "Failed to queue the media processing task" in resp.json()["detail"]

    # Verify job record updated to FAILED with dispatch message in DB
    db = SessionLocal()
    job = db.query(ProcessingJob).filter(ProcessingJob.media_id == media_id).first()
    assert job is not None
    assert job.status == JobStatus.FAILED
    assert job.error_message == "Task queue dispatch failed"
    db.close()


# 5. CELERY WORKER LIFECYCLE TESTS (EAGER EXECUTION MODE)
@patch("backend.services.processing_service.ProcessingPipeline.process_video", return_value=[])
@patch("backend.services.processing_service.storage.materialize")
@patch("backend.storage.manager.storage.exists", return_value=True)
def test_worker_lifecycle_success(mock_exists, mock_mat, mock_process_video, celery_eager):
    mock_context = MagicMock()
    mock_context.__enter__.return_value = Path(__file__)
    mock_mat.return_value = mock_context

    db = SessionLocal()
    user, project, media = create_test_user_project_media(db, "wk_ok")
    job = job_manager.create_job(db, media_id=media.id, user_id=user.id)
    db.close()

    # Trigger Celery task (ran synchronously in eager mode due to conftest fixture)
    process_video_task.delay(job.job_id)

    # Verify state updated to COMPLETED (process_job mock returned success)
    db = SessionLocal()
    job_db = job_manager.get_job(db, job.job_id)
    assert job_db.status == JobStatus.COMPLETED
    db.close()


@patch("backend.services.processing_service.ProcessingPipeline.process_video", side_effect=ValueError("Pipeline extraction error"))
@patch("backend.services.processing_service.storage.materialize")
@patch("backend.storage.manager.storage.exists", return_value=True)
def test_worker_lifecycle_pipeline_failure(mock_exists, mock_mat, mock_process_video, celery_eager):
    mock_context = MagicMock()
    mock_context.__enter__.return_value = Path(__file__)
    mock_mat.return_value = mock_context

    db = SessionLocal()
    user, project, media = create_test_user_project_media(db, "wk_fail")
    job = job_manager.create_job(db, media_id=media.id, user_id=user.id)
    db.close()

    # Trigger Celery task (raises ValueError)
    with pytest.raises(ValueError):
        process_video_task.delay(job.job_id)

    # Verify state updated to FAILED with safe message
    db = SessionLocal()
    job_db = job_manager.get_job(db, job.job_id)
    assert job_db.status == JobStatus.FAILED
    assert job_db.error_message == "An unexpected error occurred during processing."
    db.close()


@patch("backend.storage.manager.storage.exists", return_value=False)
def test_worker_lifecycle_missing_storage_file(mock_exists, celery_eager):
    db = SessionLocal()
    user, project, media = create_test_user_project_media(db, "wk_missing_file")
    job = job_manager.create_job(db, media_id=media.id, user_id=user.id)
    db.close()

    # Trigger Celery task
    process_video_task.delay(job.job_id)

    # Verify state updated to FAILED
    db = SessionLocal()
    job_db = job_manager.get_job(db, job.job_id)
    assert job_db.status == JobStatus.FAILED
    assert job_db.error_message == "Source media file not found in storage"
    db.close()


# 6. STORAGE MATERIALIZATION & CLEANUP
@patch("backend.services.processing_service.ProcessingPipeline.process_video", return_value=[])
def test_worker_local_storage_materialization(mock_pipeline, celery_eager):
    db = SessionLocal()
    user, project, media = create_test_user_project_media(db, "wk_mat")
    job = job_manager.create_job(db, media_id=media.id, user_id=user.id)
    
    # Write a dummy local storage file
    from backend.core.config import settings
    storage_root = Path(settings.LOCAL_STORAGE_ROOT)
    storage_root.mkdir(exist_ok=True)
    local_file = storage_root / media.storage_path
    local_file.parent.mkdir(parents=True, exist_ok=True)
    local_file.write_bytes(b"dummy local video data")
    db.close()

    try:
        # Trigger Celery task
        process_video_task.delay(job.job_id)

        # Verify pipeline received actual local materialized path, NOT storage key
        called_path = mock_pipeline.call_args[1]["video_path"]
        assert isinstance(called_path, str)
        assert Path(called_path).as_posix().endswith(media.storage_path)
        assert Path(called_path).exists() is True

    finally:
        if local_file.exists():
            os.remove(local_file)


@patch("backend.services.processing_service.ProcessingPipeline.process_video", return_value=[])
@patch("boto3.client")
def test_worker_r2_storage_materialization_and_cleanup(mock_boto, mock_pipeline, celery_eager):
    # Mock R2 responses
    mock_s3 = MagicMock()
    mock_boto.return_value = mock_s3
    mock_response = {"Body": MagicMock()}
    mock_response["Body"].iter_chunks.return_value = [b"r2 chunk data"]
    mock_s3.get_object.return_value = mock_response
    mock_s3.head_object.return_value = {}

    db = SessionLocal()
    user, project, media = create_test_user_project_media(db, "wk_r2")
    job = job_manager.create_job(db, media_id=media.id, user_id=user.id)
    db.close()

    # Create R2Storage instance
    r2_backend = R2Storage("https://dummy.r2.com", "bucket", "key", "secret")

    saved_temp_path = None
    def process_video_capture(self, video_path, output_directory):
        nonlocal saved_temp_path
        saved_temp_path = Path(video_path)
        assert saved_temp_path.exists() is True
        assert saved_temp_path.read_bytes() == b"r2 chunk data"
        return []

    # Patch storage in all modules where it is imported directly
    with patch("backend.services.processing_service.storage", r2_backend), \
         patch("backend.jobs.tasks.video_processing.storage", r2_backend), \
         patch("backend.storage.manager.storage", r2_backend):
         
        with patch("backend.services.processing_service.ProcessingPipeline.process_video", process_video_capture):
            process_video_task.delay(job.job_id)

    # Verify temporary file cleaned up
    assert saved_temp_path is not None
    assert saved_temp_path.exists() is False
