import os
import threading
from pathlib import Path

from faster_whisper import WhisperModel

from backend.processing.ffmpeg.service import FFmpegService

_whisper_model = None
_whisper_lock = threading.Lock()


def _get_whisper_model() -> WhisperModel:
    global _whisper_model
    if _whisper_model is None:
        with _whisper_lock:
            if _whisper_model is None:
                _whisper_model = WhisperModel(
                    "base",
                    device="cpu",
                    compute_type="int8",
                )
    return _whisper_model


class WhisperService:
    def __init__(self):
        self.model = _get_whisper_model()
        self.ffmpeg = FFmpegService()

    def transcribe(self, video_path: str) -> dict:
        video = Path(video_path)

        if not video.exists():
            raise FileNotFoundError(f"{video} does not exist.")

        audio_path = (
            video.parent
            / f"{video.stem}_audio.wav"
        )

        try:
            self.ffmpeg.extract_audio(
                str(video),
                str(audio_path),
            )

            segments, info = self.model.transcribe(
                str(audio_path),
                beam_size=1,
            )

            transcript = []

            for segment in segments:
                transcript.append(
                    {
                        "start": segment.start,
                        "end": segment.end,
                        "text": segment.text.strip(),
                    }
                )

            return {
                "language": info.language,
                "duration": info.duration,
                "segments": transcript,
            }
        finally:
            if audio_path.exists():
                try:
                    os.remove(audio_path)
                except Exception:
                    pass
