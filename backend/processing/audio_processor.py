import os
import subprocess
from pathlib import Path


class AudioProcessor:
    """
    Extracts or converts any input video/audio file into a standardized
    16kHz mono 16-bit PCM WAV file required by Speech-to-Text & Diarization engines.
    """

    @staticmethod
    def extract_audio(input_path: str | Path, output_wav_path: str | Path) -> str:
        input_str = str(input_path)
        output_str = str(output_wav_path)

        os.makedirs(os.path.dirname(output_str), exist_ok=True)

        command = [
            "ffmpeg",
            "-y",
            "-i",
            input_str,
            "-vn",
            "-acodec",
            "pcm_s16le",
            "-ar",
            "16000",
            "-ac",
            "1",
            output_str,
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"FFmpeg audio extraction failed (exit code {result.returncode}): "
                f"{result.stderr.strip() or 'No stderr output'}"
            )

        if not os.path.exists(output_str) or os.path.getsize(output_str) == 0:
            raise RuntimeError(
                "FFmpeg produced no output file or an empty WAV file."
            )

        return output_str
