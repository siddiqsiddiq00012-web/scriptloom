import sys
from typing import Any
from pydantic import ValidationError, field_validator
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
    ALLOWED_ORIGINS: Any

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v: Any) -> list[str]:
        if isinstance(v, str):
            try:
                import json
                decoded = json.loads(v)
                if isinstance(decoded, list):
                    return [str(item).strip() for item in decoded]
            except json.JSONDecodeError:
                pass
            return [item.strip() for item in v.split(",") if item.strip()]
        if isinstance(v, list):
            return [str(item).strip() for item in v]
        raise ValueError("Invalid format for ALLOWED_ORIGINS")

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

    # Storage Backend Configuration
    STORAGE_BACKEND: str = "local"
    LOCAL_STORAGE_ROOT: str = "media"
    R2_ENDPOINT_URL: str = ""
    R2_BUCKET_NAME: str = ""
    R2_ACCESS_KEY_ID: str = ""
    R2_SECRET_ACCESS_KEY: str = ""

    @field_validator("STORAGE_BACKEND")
    @classmethod
    def validate_backend(cls, v: str) -> str:
        v_lower = v.lower()
        if v_lower not in ("local", "r2"):
            raise ValueError("STORAGE_BACKEND must be either 'local' or 'r2'")
        return v_lower

    from pydantic import model_validator
    @model_validator(mode="after")
    def validate_storage_settings(self) -> "Settings":
        backend = self.STORAGE_BACKEND.lower()
        if backend == "r2":
            missing = []
            if not self.R2_ENDPOINT_URL:
                missing.append("R2_ENDPOINT_URL")
            if not self.R2_BUCKET_NAME:
                missing.append("R2_BUCKET_NAME")
            if not self.R2_ACCESS_KEY_ID:
                missing.append("R2_ACCESS_KEY_ID")
            if not self.R2_SECRET_ACCESS_KEY:
                missing.append("R2_SECRET_ACCESS_KEY")
            if missing:
                raise ValueError(f"Missing required R2 credentials when STORAGE_BACKEND is 'r2': {', '.join(missing)}")
        elif backend == "local":
            if not self.LOCAL_STORAGE_ROOT:
                raise ValueError("LOCAL_STORAGE_ROOT must be set when STORAGE_BACKEND is 'local'")
        return self

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