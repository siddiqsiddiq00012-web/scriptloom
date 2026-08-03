import sys
import os
sys.path.insert(0, os.path.abspath("."))

from backend.db.database import engine
from backend.models.base import Base
from backend.models.progress_event import ProgressEvent
from backend.models.webhook import WebhookEndpoint, WebhookDeliveryLog, DeadLetterQueue

def migrate_event_and_webhook_tables():
    Base.metadata.create_all(bind=engine)
    print("ProgressEvent & Webhook tables migration complete!")

if __name__ == "__main__":
    migrate_event_and_webhook_tables()
