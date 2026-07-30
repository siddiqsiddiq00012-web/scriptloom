import uuid
from pathlib import Path

from fastapi import UploadFile

from backend.core.config import settings
from backend.services.validation_service import ValidationService


class StorageService:
    def __init__(self):
        self.upload_root = settings.STORAGE_DIRECTORY
        self.upload_root.mkdir(
            parents=True,
            exist_ok=True,
        )

    def save_file(
        self,
        project_id: int,
        file: UploadFile,
    ) -> tuple[str, str, int]:
        ValidationService.validate_file(file)

        project_folder = self.upload_root / str(project_id)
        project_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        extension = Path(file.filename).suffix.lower()

        unique_filename = (
            f"{uuid.uuid4()}{extension}"
        )

        destination = project_folder / unique_filename

        size = 0

        with destination.open("wb") as buffer:
            while chunk := file.file.read(1024 * 1024):
                size += len(chunk)

                ValidationService.validate_file_size(
                    size
                )

                buffer.write(chunk)

        return (
            unique_filename,
            str(destination),
            size,
        )