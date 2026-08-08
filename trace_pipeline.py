import os
import sys
import logging
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from fastapi.testclient import TestClient
from backend.main import app
from backend.db.database import SessionLocal
from backend.models.user import User
from backend.models.project import Project
from backend.models.media import Media
from backend.core.token import create_access_token
from backend.jobs.celery_app import celery_app

# Force celery to execute tasks synchronously for tracing
celery_app.conf.update(task_always_eager=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def trace_pipeline():
    client = TestClient(app)
    db = SessionLocal()
    
    # 1. Setup Data
    user = db.query(User).first()
    if not user:
        user = User(name="Trace User", email="trace@test.com", hashed_password="pw")
        db.add(user)
        db.commit()
        db.refresh(user)
        
    project = db.query(Project).filter(Project.owner_id == user.id).first()
    if not project:
        project = Project(name="Trace Project", owner_id=user.id)
        db.add(project)
        db.commit()
        db.refresh(project)
        
    media = db.query(Media).filter(Media.project_id == project.id).first()
    if not media:
        media = Media(
            project_id=project.id,
            filename="test_trace.mp4",
            storage_path="projects/test/media/test_trace.mp4",
            file_size=1024,
            status="PENDING",
            duration=120
        )
        db.add(media)
        db.commit()
        db.refresh(media)
    
    # Let's clean up existing processing jobs for this media to avoid Conflict (409)
    from backend.models.processing_job import ProcessingJob
    db.query(ProcessingJob).filter(ProcessingJob.media_id == media.id).delete()
    db.commit()

    token = create_access_token({"sub": str(user.id)})
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n--- TRACE: API Request ---")
    response = client.post("/processing/process", json={"media_id": media.id}, headers=headers)
    print("API Response:", response.status_code, response.json())
    
    print("\n--- TRACE: Verify Job in DB ---")
    job = db.query(ProcessingJob).filter(ProcessingJob.media_id == media.id).first()
    if job:
        print(f"Job exists: {job.job_id}, status: {job.status}")
    else:
        print("Job not found.")
        
    print("\n--- TRACE: Verify Media Status ---")
    db.refresh(media)
    print(f"Media status after processing: {media.status}")
    
    db.close()

if __name__ == "__main__":
    trace_pipeline()
