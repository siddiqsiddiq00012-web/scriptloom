import os

# Set dummy environment variables for tests before importing the application modules
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_scriptloom.db")
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
