import os
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Iterator

from backend.storage.base import StorageProvider, validate_storage_key


class LocalStorage(StorageProvider):
    def __init__(self, root_directory: str = "media"):
        self.root_directory = Path(root_directory).resolve()

    def _resolve_key(self, key: str) -> Path:
        validate_storage_key(key)
        
        # Legacy compatibility check
        if key.startswith("media/uploads/") or key.startswith("media/output/"):
            # Resolve relative to the repository workspace root (Path(".") resolved)
            workspace_root = Path(".").resolve()
            target_path = (workspace_root / key).resolve()
        else:
            # Canonical paths (e.g. projects/{project_id}/media/...)
            target_path = (self.root_directory / key).resolve()

        # Strict containment verification
        workspace_root = Path(".").resolve()
        is_in_root = target_path.is_relative_to(self.root_directory)
        is_in_workspace = target_path.is_relative_to(workspace_root)
        
        if not (is_in_root or is_in_workspace):
            raise ValueError(f"Path escape detected: {key}")

        return target_path

    def save_stream(self, key: str, stream: Iterator[bytes], size: int) -> None:
        filepath = self._resolve_key(key)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "wb") as f:
            for chunk in stream:
                f.write(chunk)

    def read_stream(self, key: str) -> Iterator[bytes]:
        filepath = self._resolve_key(key)
        if not filepath.exists():
            raise FileNotFoundError(f"Key not found in local storage: {key}")
        
        def _chunk_generator():
            with open(filepath, "rb") as f:
                while True:
                    chunk = f.read(8 * 1024 * 1024)  # 8MB chunking
                    if not chunk:
                        break
                    yield chunk
        return _chunk_generator()

    def delete(self, key: str) -> None:
        try:
            filepath = self._resolve_key(key)
            if filepath.exists():
                os.remove(filepath)
        except Exception as e:
            # Re-raise to ensure deletion failure is surfaced (do not silently catch)
            raise RuntimeError(f"Failed to delete local storage object: {key}") from e

    def exists(self, key: str) -> bool:
        try:
            filepath = self._resolve_key(key)
            return filepath.exists()
        except ValueError:
            return False

    @contextmanager
    def materialize(self, key: str) -> Generator[Path, None, None]:
        filepath = self._resolve_key(key)
        if not filepath.exists():
            raise FileNotFoundError(f"Key not found in local storage: {key}")
        # Yield persistent file directly; do not delete on exit
        yield filepath