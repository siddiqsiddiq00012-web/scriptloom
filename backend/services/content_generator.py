import json
import logging
from pathlib import Path
from typing import Any

from google import genai
from google.genai import types
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.models.generated_content import GeneratedContent
from backend.models.media import Media
from backend.repositories.transcript_repository import TranscriptRepository

logger = logging.getLogger("scriptloom.generation")

# Base prompt loaded once at import time
_BASE_PROMPT = Path("backend/ai/prompts/content_generation.md").read_text(encoding="utf-8")

# Per-content-type generation instructions
CONTENT_TYPE_CONFIGS: dict[str, dict[str, Any]] = {
    "linkedin_post": {
        "title_prefix": "LinkedIn Post",
        "instruction": (
            "Generate a LinkedIn post (text format, NOT carousel). "
            "Write a compelling hook in the first line, followed by a body that unpacks "
            "one key insight from the transcript. Use short paragraphs and line breaks "
            "for readability. End with a call to action or thought-provoking question. "
            "Keep it between 150-300 words. "
            "Return JSON: { \"title\": \"...\", \"body\": \"...\" }"
        ),
        "default_title": "LinkedIn Post",
    },
    "x_thread": {
        "title_prefix": "X Thread",
        "instruction": (
            "Generate an X/Twitter thread of 5-8 tweets. "
            "Tweet 1 should be a strong hook that makes people want to read the rest. "
            "Each tweet should stand on its own but build a narrative. "
            "Use specific examples from the transcript. End with a CTA or key takeaway. "
            "Keep each tweet under 280 characters. "
            "Return JSON: { \"title\": \"...\", \"tweets\": [\"1/ ...\", \"2/ ...\", ...] }"
        ),
        "default_title": "X Thread",
    },
    "instagram_caption": {
        "title_prefix": "Instagram Caption",
        "instruction": (
            "Generate an Instagram caption for a post or reel. "
            "Start with a hook line, followed by the core message in 2-3 short paragraphs. "
            "Include 5-10 relevant hashtags at the end. "
            "Keep it engaging and conversational, under 200 words. "
            "Return JSON: { \"title\": \"...\", \"caption\": \"...\", \"hashtags\": [\"#...\"] }"
        ),
        "default_title": "Instagram Caption",
    },
    "newsletter": {
        "title_prefix": "Newsletter",
        "instruction": (
            "Generate a newsletter/email in markdown format. "
            "Include a subject line, greeting, 2-3 sections with headers, "
            "a key insight section, and a sign-off. "
            "Make it 300-500 words. Write as if speaking to a loyal subscriber. "
            "Return JSON: { \"title\": \"...\", \"subject\": \"...\", \"markdown\": \"...\" }"
        ),
        "default_title": "Newsletter",
    },
    "article": {
        "title_prefix": "Blog Article",
        "instruction": (
            "Generate a blog article based on the transcript's key themes. "
            "Include a title, introduction, 3-4 sections with subheadings, "
            "and a conclusion. Use specific examples from the transcript. "
            "Keep it 500-800 words. Professional but conversational tone. "
            "Return JSON: { \"title\": \"...\", \"markdown\": \"...\" }"
        ),
        "default_title": "Blog Article",
    },
    "hook": {
        "title_prefix": "Content Hooks",
        "instruction": (
            "Generate 10 content hooks (opening lines) that could be used as "
            "social media openers, email subject lines, or article introductions. "
            "Each hook should be under 20 words and create curiosity or emotion. "
            "Based on specific claims or stories from the transcript. "
            "Return JSON: { \"title\": \"...\", \"hooks\": [\"...\", ...] }"
        ),
        "default_title": "Content Hooks",
    },
    "title": {
        "title_prefix": "Titles & Headlines",
        "instruction": (
            "Generate 10 title/headline options for content derived from this transcript. "
            "Include a mix of styles: question-based, statement, number-led, curiosity-gap. "
            "Each title should be under 70 characters. "
            "Return JSON: { \"title\": \"...\", \"titles\": [\"...\", ...] }"
        ),
        "default_title": "Titles & Headlines",
    },
    "content_idea": {
        "title_prefix": "Content Ideas",
        "instruction": (
            "Generate 8 content ideas derived from this transcript. "
            "Each idea should include a platform suggestion, a brief description, "
            "and the specific transcript topic it relates to. "
            "Return JSON: { \"title\": \"...\", \"ideas\": [{ \"platform\": \"...\", \"description\": \"...\", \"source_topic\": \"...\" }, ...] }"
        ),
        "default_title": "Content Ideas",
    },
    "video_script": {
        "title_prefix": "Video Script",
        "instruction": (
            "Generate a short-form video script (30-60 seconds). "
            "Include a hook (first 3 seconds), the main message, "
            "and a call to action. Include visual cues in brackets. "
            "Keep it punchy and conversational. "
            "Return JSON: { \"title\": \"...\", \"hook\": \"...\", \"body\": \"...\", \"cta\": \"...\", \"visual_cues\": \"...\" }"
        ),
        "default_title": "Video Script",
    },
}

# Supported content types for the frontend to know what's available
SUPPORTED_CONTENT_TYPES = list(CONTENT_TYPE_CONFIGS.keys())


class ContentGenerator:
    """Generates real AI content from transcripts using Gemini."""

    def __init__(self, db: Session):
        self.db = db
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.models = [
            "gemini-3.6-flash",
            "gemini-3.5-flash",
            "gemini-3.1-flash-lite",
            "gemini-2.0-flash",
        ]

    def generate(
        self,
        media_id: int,
        content_type: str,
        tone: str | None = None,
        audience: str | None = None,
        length: str | None = None,
        extra_instructions: str | None = None,
    ) -> GeneratedContent:
        """
        Generate a single content asset for the given media resource.
        Returns the persisted GeneratedContent row.
        """
        config = CONTENT_TYPE_CONFIGS.get(content_type)
        if not config:
            raise ValueError(f"Unsupported content type: {content_type}")

        # 1. Load media and transcript
        media = self.db.query(Media).filter(Media.id == media_id).first()
        if not media:
            raise ValueError(f"Media #{media_id} not found")

        transcript_repo = TranscriptRepository(self.db)
        transcript = transcript_repo.get_by_media_id(media_id)
        if not transcript or not transcript.full_text:
            raise ValueError(
                f"Media #{media_id} has no transcript. Transcribe the resource first."
            )

        # 2. Build the generation prompt
        prompt_parts = [_BASE_PROMPT.replace("{transcript}", transcript.full_text[:12000])]

        prompt_parts.append(config["instruction"])

        # Add optional modifiers
        modifiers = []
        if tone:
            modifiers.append(f"Use a {tone.lower()} tone.")
        if audience:
            modifiers.append(f"Write for a {audience} audience.")
        if length:
            modifiers.append(f"Aim for {length.lower()} length.")
        if extra_instructions:
            modifiers.append(f"Additional instructions: {extra_instructions}")

        if modifiers:
            prompt_parts.append(" ".join(modifiers))

        full_prompt = "\n\n".join(prompt_parts)

        # 3. Call Gemini with model fallback
        body_json = None
        title = config["default_title"]
        last_error = None

        for model in self.models:
            try:
                logger.info(f"Generating {content_type} with model {model} for media {media_id}")
                response = self.client.models.generate_content(
                    model=model,
                    contents=full_prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.85,
                        top_p=0.95,
                    ),
                )

                if not response.text:
                    raise RuntimeError("Gemini returned empty response")

                raw = response.text.strip()

                # Strip markdown fences
                if raw.startswith("```json"):
                    raw = raw[7:].strip()
                elif raw.startswith("```"):
                    raw = raw[3:].strip()
                if raw.endswith("```"):
                    raw = raw[:-3].strip()

                parsed = json.loads(raw)

                if not isinstance(parsed, dict):
                    raise ValueError("Gemini response is not a JSON object")

                # Extract title and body based on content type
                title = parsed.pop("title", config["default_title"])
                body_json = json.dumps(parsed, ensure_ascii=False)

                break

            except Exception as exc:
                logger.warning(f"Model {model} failed for {content_type}: {exc}")
                last_error = exc
                continue

        if body_json is None:
            raise RuntimeError(
                f"AI generation failed for {content_type}. All models exhausted. Last error: {last_error}"
            )

        # 4. Delete any existing asset of this type for this media, then save
        self.db.query(GeneratedContent).filter(
            GeneratedContent.media_id == media_id,
            GeneratedContent.content_type == content_type,
        ).delete()

        asset = GeneratedContent(
            media_id=media_id,
            project_id=media.project_id,
            content_type=content_type,
            title=title,
            body_json=body_json,
            status="ready",
        )
        self.db.add(asset)
        self.db.commit()
        self.db.refresh(asset)

        return asset

    def rewrite_content(
        self,
        original_body: str,
        content_type: str,
        tone: str | None = None,
        extra_instructions: str | None = None,
    ) -> str:
        """Rewrite existing content with a different tone or instructions."""
        config = CONTENT_TYPE_CONFIGS.get(content_type, {})

        prompt = (
            "You are a professional content writer. Rewrite the following content.\n\n"
            f"Content type: {content_type}\n"
        )

        if tone:
            prompt += f"New tone: {tone}\n"
        if extra_instructions:
            prompt += f"Additional instructions: {extra_instructions}\n"

        prompt += (
            f"\nOriginal content:\n{original_body}\n\n"
            "Return the rewritten content as valid JSON with the same keys as the original. "
            "Do not include a 'title' key. Only return the rewritten fields."
        )

        last_error = None
        for model in self.models:
            try:
                response = self.client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.75,
                        top_p=0.90,
                    ),
                )

                if not response.text:
                    raise RuntimeError("Gemini returned empty response")

                raw = response.text.strip()
                if raw.startswith("```json"):
                    raw = raw[7:].strip()
                elif raw.startswith("```"):
                    raw = raw[3:].strip()
                if raw.endswith("```"):
                    raw = raw[:-3].strip()

                json.loads(raw)
                return raw

            except Exception as exc:
                logger.warning(f"Model {model} failed for rewrite: {exc}")
                last_error = exc
                continue

        raise RuntimeError(f"AI rewrite failed. All models exhausted. Last error: {last_error}")
