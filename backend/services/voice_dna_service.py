from sqlalchemy.orm import Session
from backend.models.voice_dna import VoiceDNA
from backend.schemas.voice_dna import VoiceDNAUpdate


class VoiceDNAService:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_profile(self, user_id: int) -> VoiceDNA:
        profile = (
            self.db.query(VoiceDNA)
            .filter(VoiceDNA.user_id == user_id)
            .first()
        )
        if not profile:
            profile = VoiceDNA(user_id=user_id)
            self.db.add(profile)
            self.db.commit()
            self.db.refresh(profile)
        return profile

    def update_profile(self, user_id: int, update_data: VoiceDNAUpdate) -> VoiceDNA:
        profile = self.get_or_create_profile(user_id)
        
        for field, value in update_data.model_dump(exclude_unset=True).items():
            if value is not None:
                setattr(profile, field, value)

        self.db.commit()
        self.db.refresh(profile)
        return profile

    def get_system_prompt_context(self, user_id: int) -> str:
        dna = self.get_or_create_profile(user_id)
        banned = [w.strip() for w in dna.banned_words.split(",") if w.strip()]
        banned_str = ", ".join([f'"{w}"' for w in banned]) if banned else "None"

        return f"""=== CREATOR VOICE DNA RULES ===
Writing Style: {dna.writing_style}
Tone: {dna.tone}
Vocabulary & Perspective: {dna.vocabulary}
Preferred CTA Style: {dna.cta_style}
Preferred Hook Style: {dna.hook_style}
Target Avg Sentence Length: {dna.avg_sentence_length} words per sentence.
Emoji Preference: {dna.emoji_preference}
STRICT BANNED JARGON & BUZZWORDS (DO NOT USE): {banned_str}
==============================="""
