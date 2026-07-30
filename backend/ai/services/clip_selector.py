from pathlib import Path

from openai import OpenAI

from backend.core.config import settings


class ClipSelector:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
        )

        self.prompt = Path(
            "backend/ai/prompts/clip_prompt.txt"
        ).read_text(encoding="utf-8")

    def analyze_transcript(
        self,
        transcript: str,
    ):

        response = self.client.responses.create(
            model="gpt-4.1-mini",
            input=f"{self.prompt}\n\nTranscript:\n{transcript}",
        )

        return response.output_text