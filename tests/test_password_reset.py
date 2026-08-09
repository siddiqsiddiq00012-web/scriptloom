import hashlib
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from backend.main import app
from backend.db.database import SessionLocal
from backend.models.password_reset_token import PasswordResetToken
from backend.models.user import User
from backend.services.email_service import EmailDeliveryError

client = TestClient(app)

AUTH_PREFIX = "/api/v1/auth"


def _register_user():
    email = f"reset_{os.urandom(4).hex()}@scriptloom.ai"
    password = "OldPassword123!"
    r = client.post(
        f"{AUTH_PREFIX}/register",
        json={"name": "Reset Tester", "email": email, "password": password},
    )
    assert r.status_code == 201
    # The password-reset flow runs from a logged-out browser (no cookies),
    # so clear any cookies set by registration before proceeding.
    client.cookies.clear()
    return email, password


def _captured_token(mock_send):
    args, _ = mock_send.call_args
    text_body = args[2]
    match = re.search(r"(https?://\S+)", text_body)
    assert match, "reset URL not found in email body"
    url = match.group(1)
    return url.split("token=", 1)[1]


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def test_forgot_password_unknown_email_returns_generic_200():
    with patch("backend.services.email_service.send_email") as mock_send:
        r = client.post(
            f"{AUTH_PREFIX}/forgot-password",
            json={"email": "nobody@example.com"},
        )
    assert r.status_code == 200
    assert "reset link" in r.json()["message"].lower()
    mock_send.assert_not_called()


def test_full_reset_flow():
    email, old_password = _register_user()
    new_password = "NewPassword456!"

    with patch("backend.services.email_service.send_email") as mock_send:
        r = client.post(f"{AUTH_PREFIX}/forgot-password", json={"email": email})
        assert r.status_code == 200
        assert mock_send.call_count == 1
        token = _captured_token(mock_send)

    with SessionLocal() as db:
        user = db.query(User).filter(User.email == email).first()
        rows = (
            db.query(PasswordResetToken)
            .filter(PasswordResetToken.user_id == user.id)
            .all()
        )
        assert len(rows) == 1
        assert rows[0].token_hash == _token_hash(token)
        assert rows[0].token_hash != token
        assert rows[0].used_at is None

    r = client.post(
        f"{AUTH_PREFIX}/reset-password",
        json={"token": token, "new_password": new_password},
    )
    assert r.status_code == 200

    assert (
        client.post(
            f"{AUTH_PREFIX}/login",
            json={"email": email, "password": new_password},
        ).status_code
        == 200
    )
    assert (
        client.post(
            f"{AUTH_PREFIX}/login",
            json={"email": email, "password": old_password},
        ).status_code
        == 401
    )

    # Single-use: replaying the same token must fail.
    client.cookies.clear()
    assert (
        client.post(
            f"{AUTH_PREFIX}/reset-password",
            json={"token": token, "new_password": "AnotherPass123!"},
        ).status_code
        == 400
    )

    with SessionLocal() as db:
        row = (
            db.query(PasswordResetToken)
            .filter(PasswordResetToken.token_hash == _token_hash(token))
            .first()
        )
        assert row.used_at is not None


def test_latest_token_invalidates_previous():
    email, _ = _register_user()
    tokens = []
    with patch("backend.services.email_service.send_email") as mock_send:
        for _ in range(2):
            r = client.post(f"{AUTH_PREFIX}/forgot-password", json={"email": email})
            assert r.status_code == 200
            tokens.append(_captured_token(mock_send))

    assert (
        client.post(
            f"{AUTH_PREFIX}/reset-password",
            json={"token": tokens[1], "new_password": "BrandNewPass1!"},
        ).status_code
        == 200
    )
    assert (
        client.post(
            f"{AUTH_PREFIX}/reset-password",
            json={"token": tokens[0], "new_password": "AnotherPass1!"},
        ).status_code
        == 400
    )


def test_expired_token_rejected():
    email, _ = _register_user()
    with patch("backend.services.email_service.send_email") as mock_send:
        client.post(f"{AUTH_PREFIX}/forgot-password", json={"email": email})
        token = _captured_token(mock_send)

    with SessionLocal() as db:
        user = db.query(User).filter(User.email == email).first()
        row = (
            db.query(PasswordResetToken)
            .filter(PasswordResetToken.user_id == user.id)
            .first()
        )
        row.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
        db.commit()

    r = client.post(
        f"{AUTH_PREFIX}/reset-password",
        json={"token": token, "new_password": "ExpiredPass1!"},
    )
    assert r.status_code == 400


def test_reset_with_unknown_token_rejected():
    r = client.post(
        f"{AUTH_PREFIX}/reset-password",
        json={
            "token": "definitely-not-a-real-token-abcdefghijklmnop",
            "new_password": "NewPassword123!",
        },
    )
    assert r.status_code == 400


def test_reset_password_validates_min_length():
    r = client.post(
        f"{AUTH_PREFIX}/reset-password",
        json={
            "token": "some-valid-looking-token-string-123456789",
            "new_password": "12345",
        },
    )
    assert r.status_code == 422


def test_forgot_password_send_failure_still_returns_200():
    email, _ = _register_user()
    with patch(
        "backend.services.email_service.send_email",
        side_effect=EmailDeliveryError("smtp down"),
    ):
        r = client.post(f"{AUTH_PREFIX}/forgot-password", json={"email": email})
    assert r.status_code == 200

    # No dangling reset token must be left behind after a failed send.
    with SessionLocal() as db:
        user = db.query(User).filter(User.email == email).first()
        rows = (
            db.query(PasswordResetToken)
            .filter(PasswordResetToken.user_id == user.id)
            .all()
        )
        assert len(rows) == 0
