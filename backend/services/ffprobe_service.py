import json
import os
import subprocess
from pathlib import Path

from backend.schemas.video_metadata import VideoMetadata


class FFprobeService:
    @staticmethod
    def extract_metadata(file_path: str | Path) -> VideoMetadata:
        file_path_str = str(file_path)
        command = [
            "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            file_path_str,
        ]

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
            )
            data = json.loads(result.stdout)

            format_info = data.get("format", {})
            duration = float(format_info.get("duration", 0.0))
            bitrate_val = format_info.get("bit_rate")
            bitrate = int(bitrate_val) if bitrate_val else None

            # Look for video stream
            video_stream = next(
                (s for s in data.get("streams", []) if s.get("codec_type") == "video"),
                None,
            )

            # Look for audio stream if video stream absent
            audio_stream = next(
                (s for s in data.get("streams", []) if s.get("codec_type") == "audio"),
                None,
            )

            if video_stream:
                fps_parts = video_stream.get("r_frame_rate", "0/1").split("/")
                fps = (
                    float(fps_parts[0]) / float(fps_parts[1])
                    if len(fps_parts) == 2 and float(fps_parts[1]) != 0
                    else 0.0
                )
                return VideoMetadata(
                    duration=duration,
                    width=int(video_stream.get("width", 0)),
                    height=int(video_stream.get("height", 0)),
                    codec=video_stream.get("codec_name", "h264"),
                    bitrate=bitrate,
                    fps=fps,
                )
            elif audio_stream:
                return VideoMetadata(
                    duration=duration,
                    width=None,
                    height=None,
                    codec=audio_stream.get("codec_name", "aac"),
                    bitrate=bitrate,
                    fps=None,
                )
            else:
                return VideoMetadata(
                    duration=duration,
                    width=None,
                    height=None,
                    codec="unknown",
                    bitrate=bitrate,
                    fps=None,
                )

        except Exception as e:
            raise RuntimeError(
                f"ffprobe failed to extract metadata for '{file_path_str}': {e}"
            ) from e