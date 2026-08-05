from sqlalchemy.orm import Session
from backend.models.transcript import Transcript, TranscriptSegment


class TranscriptRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_media_id(self, media_id: int) -> Transcript | None:
        return (
            self.db.query(Transcript)
            .filter(Transcript.media_id == media_id)
            .first()
        )

    def create_transcript(
        self,
        media_id: int,
        language: str = "en",
        full_text: str = "",
        summary: str | None = None,
    ) -> Transcript:
        existing = self.get_by_media_id(media_id)
        if existing:
            existing.language = language
            existing.full_text = full_text
            existing.summary = summary
            existing.status = "completed"
            self.db.commit()
            self.db.refresh(existing)
            return existing

        transcript = Transcript(
            media_id=media_id,
            language=language,
            full_text=full_text,
            summary=summary,
            status="completed",
        )
        self.db.add(transcript)
        self.db.commit()
        self.db.refresh(transcript)
        return transcript

    def add_segments(
        self,
        transcript_id: int,
        segments_data: list[dict],
    ) -> list[TranscriptSegment]:
        # Clear existing segments if re-transcribing
        self.db.query(TranscriptSegment).filter(
            TranscriptSegment.transcript_id == transcript_id
        ).delete()
        self.db.commit()

        segment_objects = []
        for s in segments_data:
            seg = TranscriptSegment(
                transcript_id=transcript_id,
                speaker_label=s.get("speaker_label", "Speaker 1"),
                start_time=s.get("start_time", 0.0),
                end_time=s.get("end_time", 0.0),
                text=s.get("text", ""),
                chapter_title=s.get("chapter_title"),
                key_assertion=s.get("key_assertion"),
            )
            self.db.add(seg)
            segment_objects.append(seg)

        self.db.commit()
        for seg in segment_objects:
            self.db.refresh(seg)
        return segment_objects

    def get_segment_by_id(self, segment_id: int) -> TranscriptSegment | None:
        return (
            self.db.query(TranscriptSegment)
            .filter(TranscriptSegment.id == segment_id)
            .first()
        )

    def update_segment(
        self,
        segment: TranscriptSegment,
        speaker_label: str | None = None,
        text: str | None = None,
        chapter_title: str | None = None,
    ) -> TranscriptSegment:
        if speaker_label is not None:
            segment.speaker_label = speaker_label
        if text is not None:
            segment.text = text
        if chapter_title is not None:
            segment.chapter_title = chapter_title

        self.db.commit()
        self.db.refresh(segment)
        return segment
