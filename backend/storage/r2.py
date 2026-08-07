import tempfile
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Iterator

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from backend.storage.base import StorageProvider, validate_storage_key


class IteratorFile:
    """
    Exposes an Iterator[bytes] as a read-only file-like object for boto3 compatibility.
    """
    def __init__(self, iterator: Iterator[bytes]):
        self.iterator = iterator
        self.buffer = b""

    def read(self, size: int = -1) -> bytes:
        if not self.buffer:
            try:
                self.buffer = next(self.iterator)
            except StopIteration:
                return b""

        if size < 0 or len(self.buffer) <= size:
            data = self.buffer
            self.buffer = b""
            return data
        else:
            data = self.buffer[:size]
            self.buffer = self.buffer[size:]
            return data


class R2Storage(StorageProvider):
    def __init__(
        self,
        endpoint_url: str,
        bucket_name: str,
        access_key_id: str,
        secret_access_key: str,
    ):
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            config=Config(signature_version="s3v4"),
        )
        self.bucket_name = bucket_name

    def save_stream(self, key: str, stream: Iterator[bytes], size: int) -> None:
        validate_storage_key(key)
        try:
            # upload_fileobj uploads bytes directly via file-like IteratorFile wrapper
            self.s3_client.upload_fileobj(
                Fileobj=IteratorFile(stream),
                Bucket=self.bucket_name,
                Key=key,
            )
        except ClientError as e:
            # Do not expose internal R2 credentials/endpoint in the error message
            raise RuntimeError(f"R2 storage upload failed for key: {key}") from e

    def read_stream(self, key: str) -> Iterator[bytes]:
        validate_storage_key(key)
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            
            def _chunk_generator():
                # Stream the object in 8MB chunks without loading it all into RAM
                for chunk in response["Body"].iter_chunks(chunk_size=8 * 1024 * 1024):
                    yield chunk
            return _chunk_generator()
        except ClientError as e:
            if e.response.get("Error", {}).get("Code") == "NoSuchKey":
                raise FileNotFoundError(f"Key not found in R2 storage: {key}") from e
            raise RuntimeError(f"Failed to retrieve R2 storage stream: {key}") from e

    def delete(self, key: str) -> None:
        validate_storage_key(key)
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
        except ClientError as e:
            raise RuntimeError(f"Failed to delete R2 storage object: {key}") from e

    def exists(self, key: str) -> bool:
        validate_storage_key(key)
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except ClientError as e:
            if e.response.get("Error", {}).get("Code") == "404":
                return False
            # Return False on auth errors or missing keys
            return False

    @contextmanager
    def materialize(self, key: str) -> Generator[Path, None, None]:
        validate_storage_key(key)
        
        suffix = Path(key).suffix
        temp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
        temp_path = Path(temp_file.name)
        
        try:
            # Download R2 stream directly to local temp file chunk by chunk
            for chunk in self.read_stream(key):
                temp_file.write(chunk)
            temp_file.close()
            
            yield temp_path
        finally:
            temp_file.close()
            if temp_path.exists():
                try:
                    os.unlink(temp_path)
                except Exception:
                    pass
