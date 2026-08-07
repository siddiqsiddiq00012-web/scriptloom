from abc import ABC, abstractmethod
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Iterator


def validate_storage_key(key: str) -> None:
    """
    Centralized validation to prevent path traversal, drive escape, and leading slash/backslash issues.
    Rejects keys containing directory traversal sequences, Windows paths, colons, or absolute indicators.
    """
    if not key:
        raise ValueError("Storage key cannot be empty.")
    if ".." in key:
        raise ValueError("Path traversal ('..') is not allowed in storage keys.")
    if "\\" in key:
        raise ValueError("Backslashes ('\\') are not allowed in storage keys; use forward slashes ('/').")
    if key.startswith("/") or key.startswith("./"):
        raise ValueError("Absolute or relative prefix indicators are not allowed in storage keys.")
    if ":" in key:
        raise ValueError("Drive prefixes or colons (':') are not allowed in storage keys.")


class StorageProvider(ABC):

    @abstractmethod
    def save_stream(self, key: str, stream: Iterator[bytes], size: int) -> None:
        """
        Saves a stream of bytes to storage under the given key.
        """
        pass

    @abstractmethod
    def read_stream(self, key: str) -> Iterator[bytes]:
        """
        Returns a generator yielding chunks of bytes from storage for the given key.
        """
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """
        Deletes the object with the given key from storage.
        """
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """
        Returns True if the object with the given key exists.
        """
        pass

    @abstractmethod
    @contextmanager
    def materialize(self, key: str) -> Generator[Path, None, None]:
        """
        Context manager that yields a local seekable Path on disk.
        Guarantees cleanup of temporary files on exit.
        """
        pass