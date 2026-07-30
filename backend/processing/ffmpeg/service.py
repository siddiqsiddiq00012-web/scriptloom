import json
import subprocess
from pathlib import Path


class FFmpegService:
    def get_metadata(self, video_path: str) -> dict:
        video = Path(video_path)

        if not video.exists():
            raise FileNotFoundError(f"{video} does not exist.")

        command = [
            "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            str(video),
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
        )

        return json.loads(result.stdout)

    def extract_audio(
        self,
        video_path: str,
        output_audio_path: str,
    ) -> str:
        video = Path(video_path)

        if not video.exists():
            raise FileNotFoundError(f"{video} does not exist.")

        output = Path(output_audio_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        command = [
            "ffmpeg",
            "-y",
            "-i",
            str(video),
            "-vn",
            "-acodec",
            "pcm_s16le",
            "-ar",
            "16000",
            "-ac",
            "1",
            str(output),
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print("\n========== FFmpeg STDERR ==========")
            print(result.stderr)
            print("===================================\n")

            raise RuntimeError("FFmpeg failed to extract audio.")

        return str(output)