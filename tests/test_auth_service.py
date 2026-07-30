import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_auth_and_user_flow():
    test_email = f"creator_{os.urandom(4).hex()}@scriptloom.ai"
    test_password = "SecurePassword123!"
    test_name = "Sarah Jenkins"

    print("\n--- 1. Testing Registration ---")
    reg_response = client.post(
        "/auth/register",
        json={
            "name": test_name,
            "email": test_email,
            "password": test_password,
        },
    )
    print("Register Status:", reg_response.status_code)
    print("Register Output:", reg_response.json())

    assert reg_response.status_code == 201, f"Expected 201, got {reg_response.status_code}"
    data = reg_response.json()
    assert "access_token" in data
    assert data["user"]["email"] == test_email
    assert data["user"]["name"] == test_name

    token = data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    print("\n--- 2. Testing Authenticated /auth/me ---")
    me_response = client.get("/auth/me", headers=headers)
    print("Me Status:", me_response.status_code)
    print("Me Output:", me_response.json())

    assert me_response.status_code == 200
    assert me_response.json()["email"] == test_email

    print("\n--- 3. Testing Profile Update /users/me ---")
    updated_name = "Sarah Jenkins (B2B Founder)"
    update_response = client.put(
        "/users/me",
        json={"name": updated_name},
        headers=headers,
    )
    print("Update Status:", update_response.status_code)
    print("Update Output:", update_response.json())

    assert update_response.status_code == 200
    assert update_response.json()["name"] == updated_name

    print("\n--- 4. Testing Login ---")
    login_response = client.post(
        "/auth/login",
        json={
            "email": test_email,
            "password": test_password,
        },
    )
    print("Login Status:", login_response.status_code)
    print("Login Output:", login_response.json())

    assert login_response.status_code == 200
    assert "access_token" in login_response.json()

    print("\n--- 5. Testing Invalid Credentials ---")
    invalid_login = client.post(
        "/auth/login",
        json={
            "email": test_email,
            "password": "WrongPassword!",
        },
    )
    print("Invalid Login Status:", invalid_login.status_code)
    assert invalid_login.status_code == 401

    print("\n[SUCCESS] All Authentication & User Management Service tests PASSED!")

if __name__ == "__main__":
    test_auth_and_user_flow()
