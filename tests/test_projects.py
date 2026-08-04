import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from backend.main import app
from backend.db.database import SessionLocal
from backend.models.user import User
from backend.core.token import create_access_token

client = TestClient(app)


def test_projects_endpoints_flow():
    db = SessionLocal()
    # Ensure test user exists
    user = db.query(User).filter(User.email == "project_test_user@scriptloom.ai").first()
    if not user:
        user = User(
            name="Project Tester",
            email="project_test_user@scriptloom.ai",
            hashed_password="hashed",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    user_id = user.id
    db.close()

    token = create_access_token({"sub": str(user_id)})
    headers = {"Authorization": f"Bearer {token}"}

    # 1. POST /projects/ (Create project)
    create_response = client.post(
        "/projects/",
        json={"name": "New Test Project"},
        headers=headers,
    )
    assert create_response.status_code == 201
    project_data = create_response.json()
    assert project_data["name"] == "New Test Project"
    project_id = project_data["id"]

    # 2. GET /projects/ (List projects)
    list_response = client.get(
        "/projects/",
        headers=headers,
    )
    assert list_response.status_code == 200
    projects_list = list_response.json()
    assert len(projects_list) >= 1
    assert any(p["id"] == project_id for p in projects_list)

    # 3. GET /projects/{project_id} (Get project details)
    get_response = client.get(
        f"/projects/{project_id}",
        headers=headers,
    )
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "New Test Project"

    # 4. PATCH /projects/{project_id} (Update project name)
    patch_response = client.patch(
        f"/projects/{project_id}",
        json={"name": "Updated Test Project Name"},
        headers=headers,
    )
    assert patch_response.status_code == 200
    assert patch_response.json()["name"] == "Updated Test Project Name"

    # 5. DELETE /projects/{project_id} (Delete project)
    delete_response = client.delete(
        f"/projects/{project_id}",
        headers=headers,
    )
    assert delete_response.status_code == 204

    # Verify project is indeed deleted
    get_after_delete = client.get(
        f"/projects/{project_id}",
        headers=headers,
    )
    assert get_after_delete.status_code == 404
