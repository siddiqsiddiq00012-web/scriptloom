import json
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

def test_generation_engine_flow():
    db = SessionLocal()
    user = db.query(User).filter(User.email == "gen_creator@scriptloom.ai").first()
    if not user:
        user = User(name="Sarah Jenkins", email="gen_creator@scriptloom.ai", hashed_password="hashed")
        db.add(user)
        db.commit()
        db.refresh(user)

    project = db.query(Project).filter(Project.owner_id == user.id).first()
    if not project:
        project = Project(name="Generation Masterclass", owner_id=user.id)
        db.add(project)
        db.commit()
        db.refresh(project)

    user_id = user.id
    project_id = project.id
    db.close()

    token = create_access_token({"sub": str(user_id)})
    headers = {"Authorization": f"Bearer {token}"}

    print("\n--- 1. Uploading Audio File & Transcribing ---")
    dummy_wav_header = b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80\x3e\x00\x00\x00\x7d\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
    upload_res = client.post(
        f"api/v1/projects/{project_id}/media",
        files={"file": ("masterclass_talk.wav", dummy_wav_header, "audio/wav")},
        headers=headers,
    )
    media_id = upload_res.json()["id"]

    # Transcribe & index memory
    from unittest.mock import patch
    from tests.mock_stt_data import MOCK_STT_RESPONSE
    with patch("backend.processing.stt_engine.STTEngine.transcribe", return_value=MOCK_STT_RESPONSE):
        client.post(f"/api/v1/media/{media_id}/transcribe", headers=headers)
        
    client.post(f"/api/v1/creator-memory/index/{media_id}", headers=headers)

    print("\n--- 2. Triggering Multi-Platform Campaign Pack Generation ---")
    gen_res = client.post(f"/api/v1/generation/campaign-pack/{media_id}", headers=headers)
    print("Generation Status:", gen_res.status_code)
    print("Generated Assets Count:", gen_res.json()["count"])

    assert gen_res.status_code == 201, f"Expected 201, got {gen_res.status_code}"
    assets = gen_res.json()["assets"]
    assert len(assets) == 4

    types = [a["content_type"] for a in assets]
    print("Generated Asset Types:", types)
    assert "linkedin_carousel" in types
    assert "x_thread" in types
    assert "newsletter" in types
    assert "camera_script" in types

    print("\n--- 3. Verifying Zero-Slop Banned Words Filter ---")
    banned = ["game-changer", "synergy", "paradigm shift", "revolutionary", "unleash", "delve"]
    for asset in assets:
        body_text = asset["body_json"].lower()
        for b_word in banned:
            assert b_word not in body_text, f"Banned word '{b_word}' found in {asset['content_type']}"

    print("Zero-slop verification PASSED! No banned jargon found.")

    print("\n--- 4. Fetching Campaign Pack Assets ---")
    get_res = client.get(f"/api/v1/generation/campaign-pack/{media_id}", headers=headers)
    print("Get Pack Status:", get_res.status_code)
    assert get_res.status_code == 200
    assert get_res.json()["count"] == 4

    print("\n--- 5. Testing Asset Editing (Title & Body) ---")
    first_asset_id = assets[0]["id"]
    new_title = "LinkedIn Carousel: Spoken Expertise Moat (Edited)"
    edit_res = client.put(
        f"api/v1/generation/content/{first_asset_id}",
        json={"title": new_title},
        headers=headers,
    )
    print("Edit Status:", edit_res.status_code)
    print("Edit Title Output:", edit_res.json()["title"])
    assert edit_res.status_code == 200
    assert edit_res.json()["title"] == new_title

    print("\n[SUCCESS] All AI Generation Engine & Prompt Orchestrator tests PASSED!")

if __name__ == "__main__":
    test_generation_engine_flow()
