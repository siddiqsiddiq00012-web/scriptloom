from pathlib import Path
from typing import Callable, Optional

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
        progress_callback: Optional[Callable[[str, dict], None]] = None,
    ) -> list[dict]:
        """
        Process a video and return information about every generated clip.

        progress_callback(state, payload) is invoked at each pipeline stage,
        allowing the caller to publish progress events (e.g. via the EventBus).
        """
        output_dir = Path(output_directory)
        output_dir.mkdir(parents=True, exist_ok=True)

        if progress_callback:
            progress_callback("processing", {})

        # Step 1: Transcribe
        if progress_callback:
            progress_callback("transcribing", {})
        transcription = self.transcriber.transcribe(video_path)

        # Step 1b: Defensive guard against failed/empty transcription
        if not transcription or not transcription.get("segments"):
            raise RuntimeError("No transcript segments found to generate clips from.")

        if progress_callback:
            progress_callback("transcript_completed", {
                "segments": len(transcription["segments"]),
            })

        # Step 2: Build transcript
        transcript = "\n".join(
            f"[{i}] ({segment['start']:.2f}s - {segment['end']:.2f}s) {segment['text']}"
            for i, segment in enumerate(transcription["segments"])
        )

        # Step 3: AI clip selection
        if progress_callback:
            progress_callback("analyzing", {})
        clips = self.gemini.analyze_transcript(
            transcript=transcript,
            total_segments=len(transcription["segments"]),
        )

        # Step 4: Generate subtitles
        if progress_callback:
            progress_callback("subtitles", {})
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

            if progress_callback:
                progress_callback("extracting_clip", {
                    "index": index,
                    "total": len(clips),
                })

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

        if progress_callback:
            progress_callback("clips_extracted", {"count": len(generated)})

        return generated