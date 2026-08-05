import os
from pathlib import Path


class STTConfigurationError(Exception):
    """Raised when the transcription provider is misconfigured or libraries are missing."""
    pass


class STTTranscriptionError(Exception):
    """Raised when transcription execution fails or empty/no-speech result is produced."""
    pass


class STTEngine:
    """
    Speech-to-Text & Diarization Engine for Scriptloom.
    Transcribes audio into timestamped, speaker-attributed segments,
    and performs automated chapter topic segmentation and key assertion extraction.
    """

    def __init__(self, model_size: str = "base"):
        self.model_size = model_size
        self._model = None

    def _load_model(self):
        if self._model is None:
            try:
                from faster_whisper import WhisperModel
                self._model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
            except Exception as e:
                raise STTConfigurationError(
                    f"Failed to load Whisper model '{self.model_size}': {e}"
                ) from e

    def transcribe(self, audio_wav_path: str | Path) -> dict:
        audio_str = str(audio_wav_path)

        if not os.path.exists(audio_str):
            raise FileNotFoundError(f"Audio file not found at {audio_str}")

        self._load_model()
        raw_segments = []
        detected_language = "en"
        duration = 0.0

        try:
            segments, info = self._model.transcribe(audio_str, beam_size=5)
            detected_language = info.language
            duration = info.duration

            for s in segments:
                raw_segments.append({
                    "start": round(s.start, 2),
                    "end": round(s.end, 2),
                    "text": s.text.strip(),
                })
        except Exception as e:
            raise STTTranscriptionError(f"Whisper transcription failed: {e}") from e

        # Empty/no-speech transcription must not be considered successful
        if not raw_segments:
            raise STTTranscriptionError("No speech detected or transcription is empty.")

        # Build honest transcript segments.
        # Speaker diarization, chapter detection, and key-assertion extraction are
        # NOT implemented, so we do not fabricate them. Segments carry a neutral
        # speaker label (editable via the transcript API) and no invented structure.
        enriched_segments = []
        full_text_parts = []

        for seg in raw_segments:
            full_text_parts.append(seg["text"])

            enriched_segments.append({
                "speaker_label": "Speaker",
                "start_time": seg["start"],
                "end_time": seg["end"],
                "text": seg["text"],
                "chapter_title": None,
                "key_assertion": None,
            })

        full_text = "\n\n".join(full_text_parts)
        summary = None

        return {
            "language": detected_language,
            "duration": duration,
            "full_text": full_text,
            "summary": summary,
            "segments": enriched_segments,
        }
