import sys
from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    DEBUG: bool = False
    APP_NAME: str = "Scriptloom API"
    APP_VERSION: str = "1.0.0"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    GEMINI_API_KEY: str
    REDIS_URL: str = "redis://localhost:6379/0"
    GOOGLE_CLIENT_ID: str
    OPENAI_API_KEY: str = ""

    FFMPEG_PATH: str = "ffmpeg"
    FFPROBE_PATH: str = "ffprobe"

    WHISPER_MODEL: str = "base"

    MEDIA_FOLDER: str = "storage/media"
    OUTPUT_FOLDER: str = "storage/output"

    # Enterprise Security & Limits Configuration
    UPLOAD_MAX_SIZE: int = 4 * 1024 * 1024 * 1024  # 4GB
    FFPROBE_TIMEOUT: int = 10  # seconds

    RATE_LIMIT_ANONYMOUS: int = 30  # req/min
    RATE_LIMIT_AUTHENTICATED: int = 120  # req/min
    RATE_LIMIT_AUTH: int = 5  # req/min
    RATE_LIMIT_UPLOAD: int = 10  # req/min
    RATE_LIMIT_AI: int = 20  # req/min

    VOICE_DNA_CACHE_TTL: int = 300  # seconds
    QUOTA_CACHE_TTL: int = 60  # seconds
    USER_PROFILE_CACHE_TTL: int = 300  # seconds

    CSP_ENVIRONMENT: str = "development"  # 'development' | 'production'
    HSTS_ENABLED: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


try:
    settings = Settings()
except ValidationError as e:
    missing_fields = []
    for error in e.errors():
        field_name = error.get("loc", [None])[0]
        if field_name:
            missing_fields.append(field_name)
    
    error_msg = (
        f"[CONFIGURATION ERROR] Missing required environment variable(s): {', '.join(missing_fields)}\n"
        "Please configure them in your environment or a .env file."
    )
    raise RuntimeError(error_msg) from e