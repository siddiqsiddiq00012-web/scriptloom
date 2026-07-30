from pathlib import Path

from backend.ai.services.gemini_service import GeminiService
from backend.processing.clip_extraction.service import ClipExtractionService
from backend.processing.subtitles.service import SubtitleService
from backend.processing.transcription.service import WhisperService


class ProcessingPipeline:
    def __init__(self):
        self.transcriber = WhisperService()
        self.gemini = GeminiService()
        self.subtitle_service = SubtitleService()
        self.extractor = ClipExtractionService()

    def process_video(
        self,
        video_path: str,
        output_directory: str,
    ) -> list[dict]:
        """
        Process a video and return information about every generated clip.
        """

        output_dir = Path(output_directory)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Step 1: Transcribe
        transcription = self.transcriber.transcribe(video_path)

        # Step 2: Build transcript
        transcript = "\n".join(
            f"[{i}] ({segment['start']:.2f}s - {segment['end']:.2f}s) {segment['text']}"
            for i, segment in enumerate(transcription["segments"])
        )

        # Step 3: AI clip selection
        clips = self.gemini.analyze_transcript(
            transcript=transcript,
            total_segments=len(transcription["segments"]),
        )

        # Step 4: Generate subtitles
        subtitle_file = self.subtitle_service.generate_srt(
            transcription=transcription,
            output_path=str(output_dir / "subtitles.srt"),
        )

        generated = []

        # Step 5: Extract clips
        for index, clip in enumerate(clips, start=1):
            start_time = transcription["segments"][clip.start_segment]["start"]
            end_time = transcription["segments"][clip.end_segment]["end"]

            output_video = output_dir / f"clip_{index}.mp4"

            self.extractor.extract_clip(
                input_video=video_path,
                output_video=str(output_video),
                start=start_time,
                end=end_time,
                subtitles=subtitle_file,
            )

            generated.append(
                {
                    "title": clip.title,
                    "reason": clip.reason,
                    "start_time": start_time,
                    "end_time": end_time,
                    "output": str(output_video),
                }
            )

        return generated