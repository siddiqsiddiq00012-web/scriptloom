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
from backend.models.generated_content import GeneratedContent
from backend.core.token import create_access_token
from backend.processing.jobs.manager import job_manager

client = TestClient(app)


@pytest.fixture(scope="module")
def auth_users():
    db = SessionLocal()
    
    # Create User A
    user_a = db.query(User).filter(User.email == "usera@scriptloom.ai").first()
    if not user_a:
        user_a = User(name="User A", email="usera@scriptloom.ai", hashed_password="hashed_a")
        db.add(user_a)
        db.commit()
        db.refresh(user_a)

    # Create User B
    user_b = db.query(User).filter(User.email == "userb@scriptloom.ai").first()
    if not user_b:
        user_b = User(name="User B", email="userb@scriptloom.ai", hashed_password="hashed_b")
        db.add(user_b)
        db.commit()
        db.refresh(user_b)

    # Setup Project A for User A
    proj_a = db.query(Project).filter(Project.owner_id == user_a.id).first()
    if not proj_a:
        proj_a = Project(name="Project A", owner_id=user_a.id)
        db.add(proj_a)
        db.commit()
        db.refresh(proj_a)

    # Setup Project B for User B
    proj_b = db.query(Project).filter(Project.owner_id == user_b.id).first()
    if not proj_b:
        proj_b = Project(name="Project B", owner_id=user_b.id)
        db.add(proj_b)
        db.commit()
        db.refresh(proj_b)

    # Setup Media A for User A
    media_a = db.query(Media).filter(Media.project_id == proj_a.id).first()
    if not media_a:
        media_a = Media(project_id=proj_a.id, filename="usera_media.wav", storage_path=__file__, file_size=500)
        db.add(media_a)
        db.commit()
        db.refresh(media_a)

    # Setup Transcript & Segment A for User A
    transcript_a = db.query(Transcript).filter(Transcript.media_id == media_a.id).first()
    if not transcript_a:
        transcript_a = Transcript(media_id=media_a.id, language="en", full_text="Spoken A content", status="completed")
        db.add(transcript_a)
        db.commit()
        db.refresh(transcript_a)

    seg_a = db.query(TranscriptSegment).filter(TranscriptSegment.transcript_id == transcript_a.id).first()
    if not seg_a:
        seg_a = TranscriptSegment(transcript_id=transcript_a.id, speaker_label="Speaker 1", start_time=0.0, end_time=5.0, text="Spoken segment A")
        db.add(seg_a)
        db.commit()
        db.refresh(seg_a)

    # Setup GeneratedContent A for User A
    content_a = db.query(GeneratedContent).filter(GeneratedContent.media_id == media_a.id).first()
    if not content_a:
        content_a = GeneratedContent(project_id=proj_a.id, media_id=media_a.id, content_type="linkedin_carousel", title="Title A", body_json="Body A")
        db.add(content_a)
        db.commit()
        db.refresh(content_a)

    # Keep all IDs in local variables before closing session
    user_a_id = user_a.id
    user_b_id = user_b.id
    proj_a_id = proj_a.id
    proj_b_id = proj_b.id
    media_a_id = media_a.id
    seg_a_id = seg_a.id
    content_a_id = content_a.id

    db.close()

    # Generate tokens
    token_a = create_access_token({"sub": str(user_a_id)})
    token_b = create_access_token({"sub": str(user_b_id)})

    return {
        "headers_a": {"Authorization": f"Bearer {token_a}"},
        "headers_b": {"Authorization": f"Bearer {token_b}"},
        "user_a_id": user_a_id,
        "user_b_id": user_b_id,
        "proj_a_id": proj_a_id,
        "proj_b_id": proj_b_id,
        "media_a_id": media_a_id,
        "seg_a_id": seg_a_id,
        "content_a_id": content_a_id,
    }


def test_anonymous_requests_get_401(auth_users):
    p_id = auth_users["proj_a_id"]
    m_id = auth_users["media_a_id"]
    s_id = auth_users["seg_a_id"]
    c_id = auth_users["content_a_id"]

    # Try accessing endpoints without headers
    assert client.get(f"/api/v1/projects/{p_id}").status_code == 401
    assert client.post(f"/api/v1/projects/{p_id}/media").status_code == 401
    assert client.get(f"/api/v1/projects/media/{m_id}").status_code == 401
    assert client.get(f"/api/v1/projects/media/{m_id}/waveform").status_code == 401
    assert client.delete(f"/api/v1/projects/media/{m_id}").status_code == 401
    assert client.post(f"/api/v1/media/{m_id}/transcribe").status_code == 401
    assert client.get(f"/api/v1/media/{m_id}/transcript").status_code == 401
    assert client.put(f"/api/v1/transcripts/segments/{s_id}", json={"text": "hi"}).status_code == 401
    assert client.get(f"/api/v1/clips/project/{p_id}").status_code == 401
    assert client.post(f"/api/v1/creator-memory/index/{m_id}").status_code == 401
    assert client.post(f"/api/v1/generation/campaign-pack/{m_id}").status_code == 401
    assert client.get(f"/api/v1/generation/campaign-pack/{m_id}").status_code == 401
    assert client.put(f"/api/v1/generation/content/{c_id}", json={"title": "hi"}).status_code == 401
    assert client.get(f"/api/v1/export/content/{c_id}").status_code == 401
    assert client.get(f"/api/v1/export/campaign-pack/{m_id}").status_code == 401
    assert client.post("/api/v1/processing/process", json={"media_id": m_id}).status_code == 401
    assert client.get("/api/v1/processing/jobs/some-uuid").status_code == 401
    assert client.get(f"/api/v1/stream/progress/{m_id}").status_code == 401


def test_user_a_can_access_own_resources(auth_users):
    headers = auth_users["headers_a"]
    p_id = auth_users["proj_a_id"]
    m_id = auth_users["media_a_id"]

    # Verify User A can access their own project
    response = client.get(f"/api/v1/projects/{p_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == p_id

    # Verify User A can access their own media
    response = client.get(f"/api/v1/projects/media/{m_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == m_id


def test_user_b_receives_404_for_user_a_resources(auth_users):
    headers = auth_users["headers_b"]
    p_id = auth_users["proj_a_id"]
    m_id = auth_users["media_a_id"]
    s_id = auth_users["seg_a_id"]
    c_id = auth_users["content_a_id"]

    # User B should get 404 for User A's resources
    assert client.get(f"/api/v1/projects/{p_id}", headers=headers).status_code == 404
    assert client.get(f"/api/v1/projects/media/{m_id}", headers=headers).status_code == 404
    assert client.get(f"/api/v1/projects/media/{m_id}/waveform", headers=headers).status_code == 404
    assert client.post(f"/api/v1/media/{m_id}/transcribe", headers=headers).status_code == 404
    assert client.get(f"/api/v1/media/{m_id}/transcript", headers=headers).status_code == 404
    assert client.put(f"/api/v1/transcripts/segments/{s_id}", json={"text": "edited"}, headers=headers).status_code == 404
    assert client.get(f"/api/v1/clips/project/{p_id}", headers=headers).status_code == 404
    assert client.post(f"/api/v1/creator-memory/index/{m_id}", headers=headers).status_code == 404
    assert client.post(f"/api/v1/generation/campaign-pack/{m_id}", headers=headers).status_code == 404
    assert client.get(f"/api/v1/generation/campaign-pack/{m_id}", headers=headers).status_code == 404
    assert client.put(f"/api/v1/generation/content/{c_id}", json={"title": "hi"}, headers=headers).status_code == 404
    assert client.get(f"/api/v1/export/content/{c_id}", headers=headers).status_code == 404
    assert client.get(f"/api/v1/export/campaign-pack/{m_id}", headers=headers).status_code == 404
    assert client.post("/api/v1/processing/process", json={"media_id": m_id}, headers=headers).status_code == 404
    assert client.get(f"/api/v1/stream/progress/{m_id}", headers=headers).status_code == 404


def test_nonexistent_resource_produces_404(auth_users):
    headers = auth_users["headers_a"]
    # Large nonexistent ID
    non_id = 999999

    assert client.get(f"/api/v1/projects/{non_id}", headers=headers).status_code == 404
    assert client.get(f"/api/v1/projects/media/{non_id}", headers=headers).status_code == 404
    assert client.get(f"/api/v1/projects/media/{non_id}/waveform", headers=headers).status_code == 404
    assert client.post(f"/api/v1/media/{non_id}/transcribe", headers=headers).status_code == 404
    assert client.get(f"/api/v1/media/{non_id}/transcript", headers=headers).status_code == 404
    assert client.put(f"/api/v1/transcripts/segments/{non_id}", json={"text": "hi"}, headers=headers).status_code == 404
    assert client.get(f"/api/v1/clips/project/{non_id}", headers=headers).status_code == 404
    assert client.post(f"/api/v1/creator-memory/index/{non_id}", headers=headers).status_code == 404
    assert client.post(f"/api/v1/generation/campaign-pack/{non_id}", headers=headers).status_code == 404
    assert client.get(f"/api/v1/generation/campaign-pack/{non_id}", headers=headers).status_code == 404
    assert client.put(f"/api/v1/generation/content/{non_id}", json={"title": "hi"}, headers=headers).status_code == 404
    assert client.get(f"/api/v1/export/content/{non_id}", headers=headers).status_code == 404
    assert client.get(f"/api/v1/export/campaign-pack/{non_id}", headers=headers).status_code == 404
    assert client.post("/api/v1/processing/process", json={"media_id": non_id}, headers=headers).status_code == 404
    assert client.get(f"/api/v1/stream/progress/{non_id}", headers=headers).status_code == 404


@patch("backend.storage.manager.storage.save_stream")
@patch("backend.services.ffprobe_service.FFprobeService.extract_metadata")
def test_unauthorized_upload_has_no_file_persistence(mock_metadata, mock_save, auth_users):
    # User B trying to upload to Project A
    headers = auth_users["headers_b"]
    p_id = auth_users["proj_a_id"]

    response = client.post(
        f"api/v1/projects/{p_id}/media",
        files={"file": ("malicious.wav", b"RIFF dummy bytes", "audio/wav")},
        headers=headers
    )
    assert response.status_code == 404

    # Ensure storage save was NEVER called (validation happens before reading or writing)
    mock_save.assert_not_called()
    mock_metadata.assert_not_called()


@patch("backend.processing.stt_engine.STTEngine.transcribe")
def test_unauthorized_transcribe_does_not_invoke_stt(mock_stt, auth_users):
    # User B trying to transcribe Media A
    headers = auth_users["headers_b"]
    m_id = auth_users["media_a_id"]

    response = client.post(f"/api/v1/media/{m_id}/transcribe", headers=headers)
    assert response.status_code == 404

    # STTEngine must not be called
    mock_stt.assert_not_called()


@patch("backend.services.processing_service.ProcessingService.process_job")
def test_unauthorized_process_does_not_invoke_pipeline(mock_process, auth_users):
    # User B trying to process Media A
    headers = auth_users["headers_b"]
    m_id = auth_users["media_a_id"]

    response = client.post("/api/v1/processing/process", json={"media_id": m_id}, headers=headers)
    assert response.status_code == 404

    # Pipeline background task must not be queued
    mock_process.assert_not_called()


@patch("backend.services.generation_engine.GenerationEngine.generate_campaign_pack")
def test_unauthorized_generation_does_not_invoke_ai(mock_gen, auth_users):
    # User B trying to generate for Media A
    headers = auth_users["headers_b"]
    m_id = auth_users["media_a_id"]

    response = client.post(f"/api/v1/generation/campaign-pack/{m_id}", headers=headers)
    assert response.status_code == 404

    # AI generation should not be called
    mock_gen.assert_not_called()


@patch("backend.services.export_engine.ExportEngine.export_single_content")
def test_unauthorized_export_does_not_read_files(mock_export, auth_users):
    # User B trying to export content A
    headers = auth_users["headers_b"]
    c_id = auth_users["content_a_id"]

    response = client.get(f"/api/v1/export/content/{c_id}", headers=headers)
    assert response.status_code == 404

    # Export engine should not be called
    mock_export.assert_not_called()


def test_processing_job_ownership_enforcement(auth_users):
    headers_a = auth_users["headers_a"]
    headers_b = auth_users["headers_b"]

    # Register a mock job owned by User A using database session
    db = SessionLocal()
    try:
        job = job_manager.create_job(db, media_id=auth_users["media_a_id"], user_id=auth_users["user_a_id"])
        job_id = job.job_id
    finally:
        db.close()

    # User A can query it
    response_a = client.get(f"/api/v1/processing/jobs/{job_id}", headers=headers_a)
    assert response_a.status_code == 200
    assert response_a.json()["job_id"] == job_id

    # User B receives 404 for User A's job
    response_b = client.get(f"/api/v1/processing/jobs/{job_id}", headers=headers_b)
    assert response_b.status_code == 404


def test_cross_resource_nested_id_attacks_fail(auth_users):
    headers = auth_users["headers_b"]
    # User B's project combined with User A's media_id or segment_id
    proj_b = auth_users["proj_b_id"]
    media_a = auth_users["media_a_id"]

    # Attempt to upload to Project B using Media A's references (or verify project boundaries)
    response = client.post(
        f"api/v1/projects/{proj_b}/media",
        files={"file": ("hack.wav", b"RIFF dummy bytes", "audio/wav")},
        headers=headers
    )
    # User B owns Project B, so they can upload. But trying to access Media A directly:
    assert client.get(f"/api/v1/projects/media/{media_a}", headers=headers).status_code == 404
