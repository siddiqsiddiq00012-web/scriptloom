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

def test_transcript_engine_flow():
    db = SessionLocal()
    user = db.query(User).first()
    if not user:
        user = User(name="Test Creator", email="stt_creator@scriptloom.ai", hashed_password="hashed")
        db.add(user)
        db.commit()
        db.refresh(user)

    project = db.query(Project).filter(Project.owner_id == user.id).first()
    if not project:
        project = Project(name="STT Masterclass Project", owner_id=user.id)
        db.add(project)
        db.commit()
        db.refresh(project)

    user_id = user.id
    db.close()

    token = create_access_token({"sub": str(user_id)})
    headers = {"Authorization": f"Bearer {token}"}

    print("\n--- 1. Uploading Audio File for STT Testing ---")
    dummy_wav_header = b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80\x3e\x00\x00\x00\x7d\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
    upload_res = client.post(
        f"/projects/{project.id}/media",
        files={"file": ("masterclass_speech.wav", dummy_wav_header, "audio/wav")},
        headers=headers,
    )
    assert upload_res.status_code == 200
    media_id = upload_res.json()["id"]

    from unittest.mock import patch
    from tests.mock_stt_data import MOCK_STT_RESPONSE

    print("\n--- 2. Triggering Speech-to-Text & Topic Segmentation ---")
    with patch("backend.processing.stt_engine.STTEngine.transcribe", return_value=MOCK_STT_RESPONSE):
        transcribe_res = client.post(f"/media/{media_id}/transcribe", headers=headers)
    print("Transcribe Status:", transcribe_res.status_code)
    print("Transcribe Output:", transcribe_res.json()["summary"])

    assert transcribe_res.status_code == 201, f"Expected 201, got {transcribe_res.status_code}"
    data = transcribe_res.json()
    assert data["media_id"] == media_id
    assert len(data["segments"]) > 0

    first_segment = data["segments"][0]
    segment_id = first_segment["id"]
    print("First Segment Speaker:", first_segment["speaker_label"])
    print("First Segment Text:", first_segment["text"])

    print("\n--- 3. Fetching Diarized Transcript ---")
    get_res = client.get(f"/media/{media_id}/transcript", headers=headers)
    print("Get Transcript Status:", get_res.status_code)
    assert get_res.status_code == 200
    assert len(get_res.json()["segments"]) == len(data["segments"])

    print("\n--- 4. Testing Manual Segment Edit (Speaker & Text) ---")
    new_speaker = "Sarah Jenkins (Founder)"
    new_text = "Every single executive founder and product leader spends hours articulating domain positioning."

    update_res = client.put(
        f"/transcripts/segments/{segment_id}",
        json={
            "speaker_label": new_speaker,
            "text": new_text,
        },
        headers=headers,
    )
    print("Update Status:", update_res.status_code)
    print("Update Output:", update_res.json())

    assert update_res.status_code == 200
    assert update_res.json()["speaker_label"] == new_speaker
    assert update_res.json()["text"] == new_text

    print("\n[SUCCESS] All Speech-to-Text & Transcript Engine tests PASSED!")

if __name__ == "__main__":
    test_transcript_engine_flow()
