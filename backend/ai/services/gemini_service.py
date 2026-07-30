import json
from pathlib import Path

from google import genai
from google.genai import types

from backend.core.config import settings
from backend.models.segment_clip import SegmentClip


class GeminiService:
    def __init__(self):
        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

        self.models = [
            "gemini-3.6-flash",
            "gemini-3.5-flash",
            "gemini-3.1-flash-lite",
            "gemini-2.0-flash",
        ]

        self.prompt = Path(
            "backend/ai/prompts/clip_selection.md"
        ).read_text(encoding="utf-8")

    def analyze_transcript(
        self,
        transcript: str,
        total_segments: int,
    ) -> list[SegmentClip]:
        """
        Analyze a transcript and return validated clip suggestions.
        """

        last_error = None

        for model in self.models:
            try:
                print(f"Trying model: {model}")

                response = self.client.models.generate_content(
                    model=model,
                    contents=f"{self.prompt}\n\nTranscript:\n{transcript}",
                    config=types.GenerateContentConfig(
                        temperature=0.8,
                        top_p=0.95,
                    ),
                )

                if not response.text:
                    raise RuntimeError(
                        "Gemini returned an empty response."
                    )

                text = response.text.strip()

                if text.startswith("```json"):
                    text = text[7:].strip()
                elif text.startswith("```"):
                    text = text[3:].strip()

                if text.endswith("```"):
                    text = text[:-3].strip()

                clips_data = json.loads(text)

                if not isinstance(clips_data, list):
                    raise ValueError(
                        "Gemini response is not a JSON array."
                    )

                valid_clips = []

                for clip in clips_data:
                    try:
                        segment_clip = SegmentClip(**clip)

                        if segment_clip.start_segment < 0:
                            continue

                        if segment_clip.end_segment < segment_clip.start_segment:
                            continue

                        if segment_clip.end_segment >= total_segments:
                            continue

                        valid_clips.append(segment_clip)

                    except Exception as e:
                        print(f"Skipping invalid clip: {e}")

                if not valid_clips:
                    raise RuntimeError(
                        "Gemini returned no valid clips."
                    )

                return valid_clips

            except Exception as exc:
                print(f"❌ {model} failed: {exc}")
                last_error = exc

        raise RuntimeError(
            f"All Gemini models failed. Last error: {last_error}"
        ) from last_error