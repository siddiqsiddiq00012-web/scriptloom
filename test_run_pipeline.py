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
            
        print(f"Testing process_job for media_id={media.id}")
        
        from backend.models.processing_job import ProcessingJob
        job = db.query(ProcessingJob).filter(ProcessingJob.media_id == media.id).first()
        
        processing = ProcessingService(db)
        processing.process_job(
            job_id=job.job_id,
            video_path=media.storage_path,
        )
        print("Success!")
    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    run()
