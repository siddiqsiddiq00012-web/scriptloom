import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_cors_allowed_origin():
    # Make a request with an allowed origin
    headers = {"Origin": "http://localhost:5173"}
    response = client.get("/", headers=headers)
    
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"
    assert response.headers.get("access-control-allow-credentials") == "true"


def test_cors_blocked_origin():
    # Make a request with an unauthorized origin
    headers = {"Origin": "http://malicious.com"}
    response = client.get("/", headers=headers)
    
    assert response.status_code == 200
    # A blocked origin must NOT receive access-control-allow-origin header
    assert "access-control-allow-origin" not in response.headers


def test_cors_preflight_allowed_origin():
    # Preflight request (OPTIONS) from an allowed origin
    headers = {
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type",
    }
    response = client.options("/", headers=headers)
    
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"
    assert response.headers.get("access-control-allow-methods") is not None
    assert "POST" in response.headers.get("access-control-allow-methods")
    assert response.headers.get("access-control-allow-credentials") == "true"


def test_cors_preflight_blocked_origin():
    # Preflight request (OPTIONS) from a blocked origin
    headers = {
        "Origin": "http://malicious.com",
        "Access-Control-Request-Method": "POST",
    }
    response = client.options("/", headers=headers)
    
    # Standard CORS middleware returns 400 Bad Request or a non-CORS 200 response when preflight origin is disallowed.
    # In FastAPI's CORSMiddleware, a preflight request from a blocked origin will return a 400 Bad Request
    # or a 200 response but with NO access-control-allow-origin header.
    # Let's verify that the response either fails or lacks the CORS headers.
    assert response.status_code in [200, 400]
    assert "access-control-allow-origin" not in response.headers
