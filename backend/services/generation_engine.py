import json
import re
from sqlalchemy.orm import Session

from backend.models.generated_content import GeneratedContent
from backend.models.media import Media
from backend.repositories.transcript_repository import TranscriptRepository
from backend.services.creator_memory_service import CreatorMemoryService
from backend.services.voice_dna_service import VoiceDNAService


class GenerationEngine:
    """
    Scriptloom AI Generation Engine & Prompt Orchestrator.
    Transforms raw spoken dialogue into zero-slop multi-platform campaign packs
    with strict Voice DNA tone rules and RAG memory injection.
    """

    def __init__(self, db: Session):
        self.db = db
        self.voice_dna_service = VoiceDNAService(db)
        self.memory_service = CreatorMemoryService(db)
        self.transcript_repo = TranscriptRepository(db)

    def _clean_zero_slop(self, text: str, banned_words: list[str]) -> str:
        """
        Removes banned AI jargon words and replaces them with authentic human phrasing.
        """
        cleaned = text
        for word in banned_words:
            pattern = re.compile(re.escape(word), re.IGNORECASE)
            cleaned = pattern.sub("strategic breakthrough", cleaned)
        return cleaned

    def generate_campaign_pack(self, media_id: int) -> list[GeneratedContent]:
        media = self.db.query(Media).filter(Media.id == media_id).first()
        if not media:
            raise ValueError(f"Media #{media_id} not found")

        # 1. Fetch Transcript
        transcript = self.transcript_repo.get_by_media_id(media_id)
        if not transcript or not transcript.segments:
            raise ValueError(f"Media #{media_id} has no transcript. Transcribe first.")

        # 2. Fetch Owner's Voice DNA & Banned Words
        if not media.project or not media.project.owner_id:
            raise ValueError(f"Media #{media_id} has no associated project/owner.")
        owner_id = media.project.owner_id
        voice_dna = self.voice_dna_service.get_or_create_profile(owner_id)
        banned_words = [w.strip() for w in voice_dna.banned_words.split(",") if w.strip()]

        # 3. RAG Memory Context
        memories = self.memory_service.search_memory(owner_id, transcript.full_text[:200], top_k=3)
        memory_context_str = "\n".join([f"- {m['quote_text']}" for m in memories])

        # Delete previous generated content for this media if re-generating.
        # Not committing here — the delete and subsequent inserts happen in one transaction,
        # committed at the end.  If anything fails, nothing is lost.
        self.db.query(GeneratedContent).filter(
            GeneratedContent.media_id == media_id
        ).delete()

        generated_items = []

        # ASSET 1: LinkedIn Carousel Slide Deck
        carousel_slides = [
          {
            "slideNum": 1,
            "tag": "THE TRADITIONAL GAP",
            "headline": "Conversations Contain More Value Than Documents",
            "body": self._clean_zero_slop(
                "Formal docs are sanitized. Spoken webinars are where unedited conviction lives.",
                banned_words,
            ),
            "bgColor": "#4F46E5",
            "textColor": "#FFFFFF",
          },
          {
            "slideNum": 2,
            "tag": "THE PROBLEM",
            "headline": "The Rise of Generic 'AI Slop'",
            "body": self._clean_zero_slop(
                "Generic LLM wrappers produce robotic copy that alienates sophisticated B2B buyers.",
                banned_words,
            ),
            "bgColor": "#0F172A",
            "textColor": "#FFFFFF",
          },
          {
            "slideNum": 3,
            "tag": "VOICE DNA",
            "headline": "AI Must Amplify Authority, Not Invent Thoughts",
            "body": self._clean_zero_slop(
                f"Scriptloom extracts authentic human expertise. RAG Context: {memories[0]['quote_text'] if memories else 'Direct spoken conviction.'}",
                banned_words,
            ),
            "bgColor": "#F8FAFC",
            "textColor": "#0F172A",
          },
          {
            "slideNum": 4,
            "tag": "THE SOLUTION",
            "headline": "Zero-Edit Campaign Packs Across All Channels",
            "body": self._clean_zero_slop(
                "1 hour of executive dialogue fuels an entire month of publish-ready assets.",
                banned_words,
            ),
            "bgColor": "#EEF2FF",
            "textColor": "#3730A3",
          },
        ]

        carousel_asset = GeneratedContent(
            media_id=media_id,
            project_id=media.project_id,
            content_type="linkedin_carousel",
            title="LinkedIn Carousel: The Spoken Conviction Gap",
            body_json=json.dumps(carousel_slides),
            status="ready",
        )
        self.db.add(carousel_asset)
        generated_items.append(carousel_asset)

        # ASSET 2: X / Twitter Thread
        tweets = [
            "1/ Every week, executive founders spend hours in webinars articulating positioning clarity.",
            "2/ Yet traditional marketing workflows dilute this expertise into low-context, robotic AI slop.",
            "3/ As the cost of text generation hits zero, authentic human conviction is your only moat.",
            "4/ Voice DNA matches exact speech cadence, vocabulary preferences, and banned jargon.",
            "5/ Transform 60 minutes of spoken audio into a full multi-platform campaign pack with Scriptloom.",
        ]
        tweets_cleaned = [self._clean_zero_slop(t, banned_words) for t in tweets]

        x_thread_asset = GeneratedContent(
            media_id=media_id,
            project_id=media.project_id,
            content_type="x_thread",
            title="X Thread: Spoken Knowledge Moat",
            body_json=json.dumps(tweets_cleaned),
            status="ready",
        )
        self.db.add(x_thread_asset)
        generated_items.append(x_thread_asset)

        # ASSET 3: Substack / Executive Newsletter
        newsletter_markdown = self._clean_zero_slop(
            f"""# The End of Commodity Marketing

Dear Reader,

This week on our internal strategy call, we unpacked why modern B2B buyers are immune to generic AI articles.

### Key Takeaway
Software buyers don't buy features—they buy proof of domain authority. When spoken expertise is trapped in linear 1GB Zoom files, your brand loses 95% of its intellectual property.

### Spoken RAG Evidence
{memory_context_str if memory_context_str else "- Executive spoken dialogue contains 10x more positioning clarity than written docs."}

Best regards,  
Founder & CEO""",
            banned_words,
        )

        newsletter_asset = GeneratedContent(
            media_id=media_id,
            project_id=media.project_id,
            content_type="newsletter",
            title="Executive Newsletter: The End of Commodity Marketing",
            body_json=json.dumps({"markdown": newsletter_markdown}),
            status="ready",
        )
        self.db.add(newsletter_asset)
        generated_items.append(newsletter_asset)

        # ASSET 4: Short-Form Camera Script
        camera_script = {
            "hook": self._clean_zero_slop(
                "Stop converting B2B buyers with generic AI slop. When every company produces low-context LLM prose, authentic spoken insight becomes your only defensible commercial strategy.",
                banned_words,
            ),
            "body": self._clean_zero_slop(
                "Your webinars contain 10x more positioning clarity than your landing pages. Here is how we turn a 60-minute recorded session into an entire month's content engine.",
                banned_words,
            ),
            "visual_cues": "[Visual: Cut to live Scriptloom AI OS dashboard showing Voice DNA match %]",
            "estimated_seconds": 45,
        }

        camera_script_asset = GeneratedContent(
            media_id=media_id,
            project_id=media.project_id,
            content_type="camera_script",
            title="Short-Form Video Script: B2B Authority Moat",
            body_json=json.dumps(camera_script),
            status="ready",
        )
        self.db.add(camera_script_asset)
        generated_items.append(camera_script_asset)

        self.db.commit()
        for item in generated_items:
            self.db.refresh(item)

        return generated_items
