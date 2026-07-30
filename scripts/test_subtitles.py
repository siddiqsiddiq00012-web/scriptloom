from backend.processing.subtitles.service import SubtitleService
from backend.processing.transcription.service import WhisperService

VIDEO_PATH = "sample.mp4"

print("Transcribing video...")

transcriber = WhisperService()
transcription = transcriber.transcribe(VIDEO_PATH)

subtitle_service = SubtitleService()

output = subtitle_service.generate_srt(
    transcription=transcription,
    output_path="storage/output/sample.srt",
)

print(f"\nSubtitle file created:\n{output}")