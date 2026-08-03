import os
import subprocess
from typing import Tuple
from fastapi import HTTPException, status
from backend.core.config import settings

# Recognized magic byte signatures
MAGIC_SIGNATURES = [
    b"RIFF",  # WAV / AVI
    b"ftyp",  # MP4 / MOV / M4A (offset 4)
    b"ID3",   # MP3 with ID3 header
    b"\xff\xfb", # MP3 raw audio
    b"\xff\xf3", # MP3 raw audio
    b"OggS",  # OGG / FLAC
    b"\x1a\x45\xdf\xa3", # MKV / WEBM (EBML)
]

BANNED_EXTENSIONS = [".exe", ".bat", ".cmd", ".sh", ".py", ".js", ".vbs", ".msi", ".dll", ".so", ".php"]


class FileSanitizer:
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        base = os.path.basename(filename)
        # Check double extensions e.g. song.mp3.exe
        parts = base.split(".")
        if len(parts) > 2:
            for ext in parts[1:]:
                if f".{ext.lower()}" in BANNED_EXTENSIONS:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Security violation: Executable extension '.{ext}' detected in double extension.",
                    )
        ext = os.path.splitext(base)[1].lower()
        if ext in BANNED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Security violation: Banned file extension '{ext}'.",
            )
        return base

    @staticmethod
    def validate_magic_bytes(file_bytes: bytes):
        if len(file_bytes) < 12:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File content too small to verify binary header signature.",
            )

        header = file_bytes[:32]
        matched = False
        for sig in MAGIC_SIGNATURES:
            if sig in header:
                matched = True
                break

        if not matched:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Security violation: Invalid media binary magic bytes header.",
            )

    @staticmethod
    def validate_ffprobe(file_path: str) -> Tuple[bool, str]:
        if not os.path.exists(file_path):
            return False, "File does not exist"

        cmd = [
            settings.FFPROBE_PATH,
            "-v", "error",
            "-show_entries", "format=duration,format_name",
            "-of", "default=noprint_wrappers=1:nokey=1",
            file_path,
        ]
        try:
            res = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=settings.FFPROBE_TIMEOUT,
            )
            if res.returncode == 0 and res.stdout.strip():
                return True, "Valid media"
            return False, res.stderr.strip() or "Failed to parse media container"
        except Exception as exc:
            return False, str(exc)
