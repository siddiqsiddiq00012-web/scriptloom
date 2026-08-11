import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from backend.main import app
from backend.db.database import SessionLocal
from backend.models.user import User
from backend.models.project import Project
from backend.core.token import create_access_token

client = TestClient(app)

def test_media_pipeline_flow():
    db = SessionLocal()
    # 1. Setup Test User & Project
    user = db.query(User).first()
    if not user:
        user = User(name="Test Creator", email="creator@scriptloom.ai", hashed_password="hashed")
        db.add(user)
        db.commit()
        db.refresh(user)

    project = db.query(Project).filter(Project.owner_id == user.id).first()
    if not project:
        project = Project(name="Masterclass Webinar Project", owner_id=user.id)
        db.add(project)
        db.commit()
        db.refresh(project)

    user_id = user.id
    db.close()

    token = create_access_token({"sub": str(user_id)})
    headers = {"Authorization": f"Bearer {token}"}

    print("\n--- 1. Testing Unsupported Extension Rejection ---")
    bad_upload = client.post(
        f"api/v1/projects/{project.id}/media",
        files={"file": ("malicious_script.exe", b"binary_data", "application/octet-stream")},
        headers=headers,
    )
    print("Bad Upload Status:", bad_upload.status_code)
    assert bad_upload.status_code == 400

    print("\n--- 2. Testing Audio File Upload & Processing Pipeline ---")
    dummy_wav_header = b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80\x3e\x00\x00\x00\x7d\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
    upload_response = client.post(
        f"api/v1/projects/{project.id}/media",
        files={"file": ("webinar_recording.wav", dummy_wav_header, "audio/wav")},
        headers=headers,
    )
    print("Upload Status:", upload_response.status_code)
    print("Upload Output:", upload_response.json())

    assert upload_response.status_code == 200, f"Expected 200, got {upload_response.status_code}"
    media_data = upload_response.json()
    media_id = media_data["id"]
    assert media_data["status"] == "processed"

    print("\n--- 3. Testing Get Media & Waveform JSON ---")
    media_get = client.get(f"/api/v1/projects/media/{media_id}", headers=headers)
    print("Media Get Status:", media_get.status_code)
    assert media_get.status_code == 200
    assert media_get.json()["id"] == media_id

    waveform_get = client.get(f"/api/v1/projects/media/{media_id}/waveform", headers=headers)
    print("Waveform Status:", waveform_get.status_code)
    print("Waveform Output (first 5 peaks):", waveform_get.json()["peaks"][:5])
    assert waveform_get.status_code == 200
    assert len(waveform_get.json()["peaks"]) == 100

    print("\n--- 4. Testing Media Deletion ---")
    del_response = client.delete(f"/api/v1/projects/media/{media_id}", headers=headers)
    print("Delete Status:", del_response.status_code)
    assert del_response.status_code == 200

    print("\n[SUCCESS] All Upload & Media Processing Pipeline Service tests PASSED!")

if __name__ == "__main__":
    test_media_pipeline_flow()
