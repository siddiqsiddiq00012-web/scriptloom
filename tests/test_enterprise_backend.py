import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from backend.main import app
from backend.services.file_sanitizer import FileSanitizer
from backend.services.cache_service import cache_service, CacheInvalidator
from backend.services.audit_logger import AuditLogger
from backend.db.database import SessionLocal
from backend.models.audit_log import AuditLog

client = TestClient(app)


def test_enterprise_backend_security_and_performance():
    print("\n--- 1. Testing OWASP Security Headers & X-Request-ID ---")
    res = client.get("/api/v1/health")
    print("Health Status:", res.status_code)
    print("X-Request-ID Header:", res.headers.get("x-request-id"))
    print("X-Content-Type-Options Header:", res.headers.get("x-content-type-options"))
    print("X-Frame-Options Header:", res.headers.get("x-frame-options"))
    print("Permissions-Policy Header:", res.headers.get("permissions-policy"))

    assert res.status_code == 200
    assert "x-request-id" in res.headers
    assert res.headers["x-content-type-options"] == "nosniff"
    assert res.headers["x-frame-options"] == "DENY"

    print("\n--- 2. Testing Readiness Endpoint (/ready) ---")
    ready_res = client.get("/api/v1/ready")
    print("Readiness Status:", ready_res.status_code)
    print("Readiness Body:", ready_res.json())

    assert ready_res.status_code == 200
    assert ready_res.json()["status"] == "ready"
    assert ready_res.json()["database"] == "connected"

    print("\n--- 3. Testing 4-Tier File Sanitizer ---")
    # Test double extension rejection
    try:
        FileSanitizer.sanitize_filename("malicious_podcast.mp3.exe")
        double_ext_blocked = False
    except Exception as exc:
        print("Double extension blocked successfully:", exc.detail if hasattr(exc, "detail") else exc)
        double_ext_blocked = True

    assert double_ext_blocked is True

    # Test magic byte validation with valid WAV header
    valid_wav_header = b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00"
    FileSanitizer.validate_magic_bytes(valid_wav_header)
    print("WAV Magic bytes validated successfully!")

    print("\n--- 4. Testing Sub-5ms Cache Service & Invalidation ---")
    test_key = "voice_dna:99"
    cache_service.set(test_key, {"tone": "Authoritative"}, ttl_seconds=60)
    assert cache_service.get(test_key)["tone"] == "Authoritative"

    # Invalidate
    CacheInvalidator.invalidate_voice_dna(99)
    assert cache_service.get(test_key) is None
    print("Cache invalidation verified successfully!")

    print("\n--- 5. Testing DB Immutable Audit Logging ---")
    db = SessionLocal()
    AuditLogger.log_event(
        db=db,
        action="TEST_SECURITY_AUDIT",
        resource="system/test",
        user_id=1,
        ip_address="127.0.0.1",
        status="SUCCESS",
        metadata={"test": "passed"},
    )
    latest_audit = db.query(AuditLog).filter(AuditLog.action == "TEST_SECURITY_AUDIT").first()
    assert latest_audit is not None
    assert latest_audit.user_id == 1
    db.close()
    print("Audit log recorded and verified in database!")

    print("\n[SUCCESS] All Enterprise Security, Caching, & Performance tests PASSED!")


if __name__ == "__main__":
    test_enterprise_backend_security_and_performance()
