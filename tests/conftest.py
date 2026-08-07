import os
from unittest.mock import patch

# Globally patch the rate limiter to never rate limit during test execution
patch("backend.middleware.rate_limiter.MemoryRateLimiter.is_rate_limited", return_value=(False, 9999, 0)).start()

# Set dummy environment variables for tests before importing the application modules
os.environ["DATABASE_URL"] = "sqlite:///./test_scriptloom.db"
os.environ["ALLOWED_ORIGINS"] = "http://localhost:5173,http://localhost:5174,http://example.com"
os.environ.setdefault(
    "SECRET_KEY",
    "test-secret-key-for-unit-tests-only-must-be-long-enough-32-chars"
)
os.environ.setdefault("GEMINI_API_KEY", "test-gemini-api-key-placeholder")
os.environ.setdefault(
    "GOOGLE_CLIENT_ID",
    "895652265626-9u3ala8rn0hpdtrjgbdeh116ukvi8cv5.apps.googleusercontent.com"
)

# Ensure all SQLite tables are created for direct session queries prior to running tests
from backend.db.database import engine
from backend.models import Base
Base.metadata.create_all(bind=engine)

import pytest
from backend.jobs.celery_app import celery_app

@pytest.fixture
def celery_eager():
    """Fixture to temporarily enable eager execution mode for Celery tasks in tests."""
    original_eager = celery_app.conf.task_always_eager
    original_propagate = celery_app.conf.task_eager_propagates
    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = True
    yield
    celery_app.conf.task_always_eager = original_eager
    celery_app.conf.task_eager_propagates = original_propagate
