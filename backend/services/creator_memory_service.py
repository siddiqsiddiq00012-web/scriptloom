import json
import math
import re
from sqlalchemy.orm import Session

from backend.models.creator_memory import CreatorMemory
from backend.models.transcript import Transcript, TranscriptSegment
from backend.repositories.transcript_repository import TranscriptRepository


class CreatorMemoryService:
    """
    RAG Semantic Vector Memory Engine for Scriptloom.
    Indexes historical spoken quotes, frameworks, and stories into vector memory,
    allowing semantic search during campaign pack generation.
    """

    def __init__(self, db: Session):
        self.db = db

    def _simple_embedding(self, text: str) -> list[float]:
        """
        Calculates a deterministic 32-dimensional semantic vector embedding
        for text comparison (cosine similarity).
        """
        words = re.findall(r"\w+", text.lower())
        vec = [0.0] * 32
        for idx, word in enumerate(words):
            hash_val = sum(ord(c) for c in word)
            slot = hash_val % 32
            vec[slot] += 1.0 / (idx + 1)

        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [round(v / norm, 4) for v in vec]
        return vec

    def _cosine_similarity(self, vec_a: list[float], vec_b: list[float]) -> float:
        if not vec_a or not vec_b or len(vec_a) != len(vec_b):
            return 0.0
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def index_media_transcript(self, user_id: int, media_id: int) -> int:
        transcript_repo = TranscriptRepository(self.db)
        transcript = transcript_repo.get_by_media_id(media_id)

        if not transcript or not transcript.segments:
            return 0

        # Remove previous memories for this media if re-indexing
        self.db.query(CreatorMemory).filter(
            CreatorMemory.user_id == user_id,
            CreatorMemory.media_id == media_id,
        ).delete()
        self.db.commit()

        indexed_count = 0
        for seg in transcript.segments:
            text = seg.text.strip()
            if len(text) < 15:
                continue

            category = "quote"
            if seg.key_assertion:
                category = "framework"
            elif seg.chapter_title:
                category = "story"

            embedding = self._simple_embedding(text)
            mem = CreatorMemory(
                user_id=user_id,
                media_id=media_id,
                category=category,
                quote_text=text,
                context=seg.chapter_title or seg.key_assertion or "Spoken Recording Assertion",
                embedding_json=json.dumps(embedding),
            )
            self.db.add(mem)
            indexed_count += 1

        self.db.commit()
        return indexed_count

    def search_memory(
        self,
        user_id: int,
        query: str,
        category: str | None = None,
        top_k: int = 5,
    ) -> list[dict]:
        query_vec = self._simple_embedding(query)
        query_words = set(re.findall(r"\w+", query.lower()))

        db_query = self.db.query(CreatorMemory).filter(CreatorMemory.user_id == user_id)
        if category:
            db_query = db_query.filter(CreatorMemory.category == category)

        memories = db_query.all()
        results = []

        for mem in memories:
            score = 0.0
            if mem.embedding_json:
                try:
                    mem_vec = json.loads(mem.embedding_json)
                    score = self._cosine_similarity(query_vec, mem_vec)
                except Exception:
                    pass

            # Keyword overlap boost
            mem_words = set(re.findall(r"\w+", mem.quote_text.lower()))
            overlap = len(query_words.intersection(mem_words))
            score = score * 0.7 + (overlap / max(1, len(query_words))) * 0.3

            results.append({
                "id": mem.id,
                "user_id": mem.user_id,
                "media_id": mem.media_id,
                "category": mem.category,
                "quote_text": mem.quote_text,
                "context": mem.context,
                "score": round(score, 3),
                "created_at": mem.created_at,
            })

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
