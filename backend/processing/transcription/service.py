from pathlib import Path

from faster_whisper import WhisperModel

from backend.processing.ffmpeg.service import FFmpegService


class WhisperService:
    def __init__(self):
        self.model = WhisperModel(
            "base",
            device="cpu",
            compute_type="int8",
        )
        self.ffmpeg = FFmpegService()

    def transcribe(self, video_path: str) -> dict:
        video = Path(video_path)

        if not video.exists():
            raise FileNotFoundError(f"{video} does not exist.")

        audio_path = (
            video.parent
            / f"{video.stem}_audio.wav"
        )

        self.ffmpeg.extract_audio(
            str(video),
            str(audio_path),
        )

        segments, info = self.model.transcribe(
            str(audio_path),
            beam_size=5,
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