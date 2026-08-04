import os
import sys
from unittest.mock import patch, ANY

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from backend.main import app
from backend.core.config import settings

client = TestClient(app)

def test_google_auth_success():
    with patch.object(settings, "GOOGLE_CLIENT_ID", "test_client_id"):
        mock_id_info = {
            "iss": "https://accounts.google.com",
            "email": "user@gmail.com",
            "email_verified": True,
            "name": "Test User",
            "picture": "http://avatar.com/pic.jpg",
        }
        with patch("google.oauth2.id_token.verify_oauth2_token", return_value=mock_id_info) as mock_verify:
            response = client.post(
                "/auth/google",
                json={"credential": "mock_google_token"}
            )
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert data["user"]["email"] == "user@gmail.com"
            assert data["user"]["name"] == "Test User"
            assert data["user"]["avatar_url"] == "http://avatar.com/pic.jpg"
            mock_verify.assert_called_once_with(
                "mock_google_token",
                ANY,
                audience="test_client_id"
            )

def test_google_auth_missing_client_id():
    with patch.object(settings, "GOOGLE_CLIENT_ID", ""):
        response = client.post(
            "/auth/google",
            json={"credential": "mock_google_token"}
        )
        assert response.status_code == 500
        assert "Google OAuth configuration is missing" in response.json()["detail"]

def test_google_auth_missing_token():
    with patch.object(settings, "GOOGLE_CLIENT_ID", "test_client_id"):
        response = client.post(
            "/auth/google",
            json={"id_token": None, "token": None, "credential": None}
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Google ID Token is required."

def test_google_auth_verification_failed():
    with patch.object(settings, "GOOGLE_CLIENT_ID", "test_client_id"):
        with patch("google.oauth2.id_token.verify_oauth2_token", side_effect=ValueError("Token expired")):
            response = client.post(
                "/auth/google",
                json={"credential": "expired_token"}
            )
            assert response.status_code == 401
            assert response.json()["detail"] == "Authentication failed. Please verify your credentials."

def test_google_auth_invalid_issuer():
    with patch.object(settings, "GOOGLE_CLIENT_ID", "test_client_id"):
        mock_id_info = {
            "iss": "http://malicious-issuer.com",
            "email": "user@gmail.com",
            "email_verified": True,
            "name": "Test User",
        }
        with patch("google.oauth2.id_token.verify_oauth2_token", return_value=mock_id_info):
            response = client.post(
                "/auth/google",
                json={"credential": "mock_token"}
            )
            assert response.status_code == 401
            assert response.json()["detail"] == "Authentication failed. Please verify your credentials."

def test_google_auth_unverified_email():
    with patch.object(settings, "GOOGLE_CLIENT_ID", "test_client_id"):
        mock_id_info = {
            "iss": "accounts.google.com",
            "email": "user@gmail.com",
            "email_verified": False,
            "name": "Test User",
        }
        with patch("google.oauth2.id_token.verify_oauth2_token", return_value=mock_id_info):
            response = client.post(
                "/auth/google",
                json={"credential": "mock_token"}
            )
            assert response.status_code == 401
            assert response.json()["detail"] == "Authentication failed. Please verify your credentials."

def test_google_auth_missing_email_claim():
    with patch.object(settings, "GOOGLE_CLIENT_ID", "test_client_id"):
        mock_id_info = {
            "iss": "https://accounts.google.com",
            "email_verified": True,
            "name": "Test User",
        }
        with patch("google.oauth2.id_token.verify_oauth2_token", return_value=mock_id_info):
            response = client.post(
                "/auth/google",
                json={"credential": "mock_token"}
            )
            assert response.status_code == 401
            assert response.json()["detail"] == "Authentication failed. Please verify your credentials."

def test_google_auth_ignore_frontend_injected_claims():
    with patch.object(settings, "GOOGLE_CLIENT_ID", "test_client_id"):
        mock_id_info = {
            "iss": "https://accounts.google.com",
            "email": "legit_user@gmail.com",
            "email_verified": True,
            "name": "Legit Name",
            "picture": "http://avatar.com/legit.jpg",
        }
        with patch("google.oauth2.id_token.verify_oauth2_token", return_value=mock_id_info):
            response = client.post(
                "/auth/google",
                json={
                    "credential": "mock_token",
                    "email": "hacker@gmail.com",
                    "name": "Hacker Name",
                    "avatar_url": "http://avatar.com/hacker.jpg",
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert data["user"]["email"] == "legit_user@gmail.com"
            assert data["user"]["name"] == "Legit Name"
            assert data["user"]["avatar_url"] == "http://avatar.com/legit.jpg"
