from backend.processing.transcription.service import WhisperService

service = WhisperService()

result = service.transcribe(
    "test_videos/sample.mp4"
)

print(result)