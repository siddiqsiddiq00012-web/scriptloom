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
from backend.services.voice_dna_service import VoiceDNAService

client = TestClient(app)

def test_voice_dna_and_memory_flow():
    db = SessionLocal()
    user = db.query(User).filter(User.email == "dna_creator@scriptloom.ai").first()
    if not user:
        user = User(name="Sarah Jenkins", email="dna_creator@scriptloom.ai", hashed_password="hashed")
        db.add(user)
        db.commit()
        db.refresh(user)

    project = db.query(Project).filter(Project.owner_id == user.id).first()
    if not project:
        project = Project(name="Voice DNA Masterclass", owner_id=user.id)
        db.add(project)
        db.commit()
        db.refresh(project)

    user_id = user.id
    project_id = project.id
    db.close()

    token = create_access_token({"sub": str(user_id)})
    headers = {"Authorization": f"Bearer {token}"}

    print("\n--- 1. Fetching Voice DNA Profile ---")
    dna_get = client.get("/voice-dna/me", headers=headers)
    print("Voice DNA Get Status:", dna_get.status_code)
    print("Voice DNA Get Output:", dna_get.json())

    assert dna_get.status_code == 200
    assert dna_get.json()["user_id"] == user_id

    print("\n--- 2. Updating Voice DNA Parameters ---")
    banned_words_test = "game-changer, synergy, paradigm shift, revolutionary, unleash"
    dna_update = client.put(
        "/voice-dna/me",
        json={
            "writing_style": "Direct, authoritative B2B founder perspective",
            "banned_words": banned_words_test,
            "avg_sentence_length": 12,
        },
        headers=headers,
    )
    print("Voice DNA Update Status:", dna_update.status_code)
    print("Voice DNA Banned Words:", dna_update.json()["banned_words"])

    assert dna_update.status_code == 200
    assert dna_update.json()["banned_words"] == banned_words_test

    print("\n--- 3. Testing System Prompt Context Injection ---")
    db_session = SessionLocal()
    context = VoiceDNAService(db_session).get_system_prompt_context(user_id)
    db_session.close()
    print("System Prompt Context:\n", context)
    assert "Direct, authoritative B2B founder perspective" in context
    assert '"game-changer"' in context

    print("\n--- 4. Testing Media Upload & Transcription ---")
    dummy_wav_header = b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80\x3e\x00\x00\x00\x7d\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
    upload_res = client.post(
        f"/projects/{project_id}/media",
        files={"file": ("positioning_talk.wav", dummy_wav_header, "audio/wav")},
    )
    media_id = upload_res.json()["id"]

    # Transcribe media
    from unittest.mock import patch
    from tests.mock_stt_data import MOCK_STT_RESPONSE
    with patch("backend.processing.stt_engine.STTEngine.transcribe", return_value=MOCK_STT_RESPONSE):
        client.post(f"/media/{media_id}/transcribe")

    print("\n--- 5. Indexing Media Transcript into Creator Memory RAG Store ---")
    index_res = client.post(f"/creator-memory/index/{media_id}", headers=headers)
    print("Memory Index Status:", index_res.status_code)
    print("Memory Index Output:", index_res.json())

    assert index_res.status_code == 201
    assert index_res.json()["indexed_count"] > 0

    print("\n--- 6. Testing Semantic Vector Memory Search ---")
    search_res = client.post(
        "/creator-memory/search",
        json={
            "query": "authority positioning and campaign packs",
            "top_k": 3,
        },
        headers=headers,
    )
    print("Memory Search Status:", search_res.status_code)
    print("Memory Search Results Count:", len(search_res.json()))
    if len(search_res.json()) > 0:
        print("Top Matched Quote:", search_res.json()[0]["quote_text"])
        print("Top Similarity Score:", search_res.json()[0]["score"])

    assert search_res.status_code == 200
    assert len(search_res.json()) > 0

    print("\n[SUCCESS] All Voice DNA Engine & Creator Memory RAG Store tests PASSED!")

if __name__ == "__main__":
    test_voice_dna_and_memory_flow()
