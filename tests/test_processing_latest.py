import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

from backend.main import app
from backend.models.processing_job import ProcessingJob, JobStatus
from backend.models.media import Media
from backend.models.project import Project
from backend.models.user import User
from backend.core.token import create_access_token

@pytest.fixture
def test_users(db_session: Session):
    user_a = User(email="user_a@example.com", name="User A")
    user_b = User(email="user_b@example.com", name="User B")
    user_a.set_password("pass")
    user_b.set_password("pass")
    db_session.add(user_a)
    db_session.add(user_b)
    db_session.commit()
    db_session.refresh(user_a)
    db_session.refresh(user_b)
    return user_a, user_b

@pytest.fixture
def user_a_token(test_users):
    user_a, _ = test_users
    return create_access_token(data={"sub": str(user_a.id)})

@pytest.fixture
def user_b_token(test_users):
    _, user_b = test_users
    return create_access_token(data={"sub": str(user_b.id)})

@pytest.fixture
def test_media(db_session: Session, test_users):
    user_a, _ = test_users
    project = Project(name="Project A", owner_id=user_a.id)
    db_session.add(project)
    db_session.commit()
    
    media = Media(project_id=project.id, filename="test.mp4", status="COMPLETED")
    db_session.add(media)
    db_session.commit()
    db_session.refresh(media)
    return media

def test_get_latest_job_anonymous(client: TestClient, test_media):
    response = client.get(f"/api/v1/api/v1/processing/media/{test_media.id}/jobs/latest")
    assert response.status_code == 401

def test_get_latest_job_no_job(client: TestClient, test_media, user_a_token):
    headers = {"Authorization": f"Bearer {user_a_token}"}
    response = client.get(f"/api/v1/api/v1/processing/media/{test_media.id}/jobs/latest", headers=headers)
    assert response.status_code == 404
    assert "No processing jobs found" in response.json()["detail"]

def test_get_latest_job_unauthorized_user(client: TestClient, test_media, user_b_token):
    headers = {"Authorization": f"Bearer {user_b_token}"}
    response = client.get(f"/api/v1/api/v1/processing/media/{test_media.id}/jobs/latest", headers=headers)
    assert response.status_code == 403 # or 404 depending on verify_media_ownership sanitization

def test_get_latest_job_success_multiple_jobs(client: TestClient, db_session: Session, test_media, test_users, user_a_token):
    user_a, _ = test_users
    now = datetime.now(timezone.utc)
    
    # Old job
    job1 = ProcessingJob(
        job_id="job_old",
        media_id=test_media.id,
        user_id=user_a.id,
        status=JobStatus.FAILED,
        created_at=now - timedelta(days=1)
    )
    # New job
    job2 = ProcessingJob(
        job_id="job_new",
        media_id=test_media.id,
        user_id=user_a.id,
        status=JobStatus.PROCESSING,
        created_at=now
    )
    db_session.add_all([job1, job2])
    db_session.commit()

    headers = {"Authorization": f"Bearer {user_a_token}"}
    response = client.get(f"/api/v1/api/v1/processing/media/{test_media.id}/jobs/latest", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == "job_new"
    assert data["status"] == "PROCESSING"
