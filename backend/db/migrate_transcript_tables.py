import sys
import os
sys.path.insert(0, os.path.abspath("."))

from backend.db.database import engine
from backend.models.base import Base
from backend.models.transcript import Transcript, TranscriptSegment

def migrate_transcript_tables():
    Base.metadata.create_all(bind=engine)
    print("Transcripts and TranscriptSegments tables migration complete!")

if __name__ == "__main__":
    migrate_transcript_tables()
