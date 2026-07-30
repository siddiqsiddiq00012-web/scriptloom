from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from backend.core.config import settings


class ValidationService:
    ALLOWED_EXTENSIONS = {
        ".mp4",
        ".mov",
        ".avi",
        ".mkv",
        ".webm",
    }

    @classmethod
    def validate_file(
        cls,
        file: UploadFile,
    ):
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename is missing.",
            )

        extension = (
            Path(file.filename)
            .suffix
            .lower()
        )

        if extension not in cls.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: {extension}",
            )

    @classmethod
    def validate_file_size(
        cls,
        size: int,
    ):
        if size > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Maximum upload size exceeded.",
            )