import sys
import os
sys.path.insert(0, os.path.abspath("."))

from backend.db.database import engine
from backend.models.base import Base
from backend.models.voice_dna import VoiceDNA
from backend.models.creator_memory import CreatorMemory

def migrate_voice_dna_and_memory():
    Base.metadata.create_all(bind=engine)
    print("VoiceDNA and CreatorMemories tables migration complete!")

if __name__ == "__main__":
    migrate_voice_dna_and_memory()
