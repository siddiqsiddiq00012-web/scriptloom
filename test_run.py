import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.db.database import SessionLocal
from backend.services.processing_service import ProcessingService
from backend.models.media import Media

def run():
    db = SessionLocal()
    try:
        media = db.query(Media).first()
        if not media:
            print("No media found!")
            return
            
        print(f"Found media: {media.id} at {media.storage_path}")
    finally:
        db.close()

if __name__ == "__main__":
    run()
