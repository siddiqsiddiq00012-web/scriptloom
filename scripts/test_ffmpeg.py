from backend.processing.ffmpeg.service import FFmpegService

service = FFmpegService()

metadata = service.get_metadata(
    "test_videos/sample.mp4"
)

print(metadata)