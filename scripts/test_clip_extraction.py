from backend.processing.clip_extraction.service import ClipExtractionService

service = ClipExtractionService()

output = service.extract_clip(
    input_video="sample.mp4",
    output_video="storage/output/test_clip.mp4",
    start=3.5,
    end=14.5,
)

print(output)