import sys
import os
sys.path.insert(0, os.path.abspath("."))

from backend.db.database import engine
from backend.models.base import Base
from backend.models.generated_content import GeneratedContent

def migrate_generated_content():
    Base.metadata.create_all(bind=engine)
    print("GeneratedContent table migration complete!")

if __name__ == "__main__":
    migrate_generated_content()
