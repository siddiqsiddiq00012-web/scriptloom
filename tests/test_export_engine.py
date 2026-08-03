import io
import os
import sys
import zipfile

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from backend.main import app
from backend.db.database import SessionLocal
from backend.models.user import User
from backend.models.project import Project

client = TestClient(app)

def test_export_engine_flow():
    db = SessionLocal()
    user = db.query(User).filter(User.email == "export_creator@scriptloom.ai").first()
    if not user:
        user = User(name="Sarah Jenkins", email="export_creator@scriptloom.ai", hashed_password="hashed")
        db.add(user)
        db.commit()
        db.refresh(user)

    project = db.query(Project).filter(Project.owner_id == user.id).first()
    if not project:
        project = Project(name="Export Masterclass", owner_id=user.id)
        db.add(project)
        db.commit()
        db.refresh(project)

    project_id = project.id
    db.close()

    print("\n--- 1. Uploading Audio, Transcribing, & Generating Campaign Pack ---")
    dummy_wav_header = b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80\x3e\x00\x00\x00\x7d\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
    upload_res = client.post(
        f"/projects/{project_id}/media",
        files={"file": ("export_talk.wav", dummy_wav_header, "audio/wav")},
    )
    media_id = upload_res.json()["id"]

    client.post(f"/media/{media_id}/transcribe")
    gen_res = client.post(f"/generation/campaign-pack/{media_id}")
    assets = gen_res.json()["assets"]
    first_asset_id = assets[0]["id"]

    print("\n--- 2. Testing Single Asset Markdown Export ---")
    md_res = client.get(f"/export/content/{first_asset_id}?format=markdown")
    print("Markdown Export Status:", md_res.status_code)
    print("Content-Disposition Header:", md_res.headers.get("content-disposition"))
    assert md_res.status_code == 200
    assert md_res.headers["content-type"].startswith("text/markdown")
    assert len(md_res.content) > 0

    print("\n--- 3. Testing Single Asset Text Export ---")
    txt_res = client.get(f"/export/content/{first_asset_id}?format=txt")
    print("TXT Export Status:", txt_res.status_code)
    assert txt_res.status_code == 200
    assert txt_res.headers["content-type"].startswith("text/plain")

    print("\n--- 4. Testing Bundled Campaign Pack ZIP Export ---")
    zip_res = client.get(f"/export/campaign-pack/{media_id}")
    print("ZIP Export Status:", zip_res.status_code)
    print("ZIP Header:", zip_res.headers.get("content-type"))
    assert zip_res.status_code == 200
    assert zip_res.headers["content-type"] == "application/zip"

    # Verify Zip file entries inside in-memory bytes
    zip_file = zipfile.ZipFile(io.BytesIO(zip_res.content))
    namelist = zip_file.namelist()
    print("ZIP File Entries:", namelist)
    assert len(namelist) == 4

    print("\n[SUCCESS] All Content Management & Export Engine tests PASSED!")

if __name__ == "__main__":
    test_export_engine_flow()
