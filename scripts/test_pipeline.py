from pathlib import Path

from backend.ai.services.gemini_service import GeminiService
from backend.processing.clip_extraction.service import ClipExtractionService
from backend.processing.subtitles.service import SubtitleService
from backend.processing.transcription.service import WhisperService

VIDEO_PATH = "sample.mp4"
OUTPUT_DIR = Path("storage/output")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("Step 1: Transcribing video...")

transcriber = WhisperService()
result = transcriber.transcribe(VIDEO_PATH)

transcript = "\n".join(
    f"[{i}] ({segment['start']:.2f}s - {segment['end']:.2f}s) {segment['text']}"
    for i, segment in enumerate(result["segments"])
)

print("\nTranscript:")
print(transcript)

print("\nStep 2: Finding the best clips...")

gemini = GeminiService()
clips = gemini.analyze_transcript(
    transcript=transcript,
    total_segments=len(result["segments"]),
)

print(f"\nFound {len(clips)} clip(s).")

subtitle_service = SubtitleService()

subtitle_file = subtitle_service.generate_srt(
    transcription=result,
    output_path="storage/output/sample.srt",
)

extractor = ClipExtractionService()

for index, clip in enumerate(clips, start=1):
    start_time = result["segments"][clip.start_segment]["start"]
    end_time = result["segments"][clip.end_segment]["end"]

    output_file = OUTPUT_DIR / f"clip_{index}.mp4"

    print(f"\nCreating clip {index}")
    print(f"Title          : {clip.title}")
    print(f"Start Segment  : {clip.start_segment}")
    print(f"End Segment    : {clip.end_segment}")
    print(f"Start Time     : {start_time}")
    print(f"End Time       : {end_time}")
    print(f"Reason         : {clip.reason}")

    extractor.extract_clip(
        input_video=VIDEO_PATH,
        output_video=str(output_file),
        start=start_time,
        end=end_time,
        subtitles=subtitle_file,
    )

print("\nPipeline completed successfully!")