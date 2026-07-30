from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    DEBUG: bool = False
    APP_NAME: str = "Scriptloom API"
    APP_VERSION: str = "1.0.0"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    GEMINI_API_KEY: str = ""
    REDIS_URL: str = "redis://localhost:6379/0"

    OPENAI_API_KEY: str = ""

    FFMPEG_PATH: str = "ffmpeg"
    FFPROBE_PATH: str = "ffprobe"

    WHISPER_MODEL: str = "base"

    MEDIA_FOLDER: str = "storage/media"
    OUTPUT_FOLDER: str = "storage/output"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()