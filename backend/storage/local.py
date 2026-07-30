from pathlib import Path

from backend.storage.base import StorageProvider


UPLOAD_DIRECTORY = Path("media/uploads")


class LocalStorage(StorageProvider):

    async def save(
        self,
        filename: str,
        content: bytes,
    ) -> str:

        UPLOAD_DIRECTORY.mkdir(
            parents=True,
            exist_ok=True,
        )

        filepath = UPLOAD_DIRECTORY / filename

        filepath.write_bytes(content)

        return str(filepath)