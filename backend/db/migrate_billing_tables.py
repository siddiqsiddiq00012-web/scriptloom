import sys
import os
sys.path.insert(0, os.path.abspath("."))

from backend.db.database import engine
from backend.models.base import Base
from backend.models.billing import UserSubscription, UsageRecord

def migrate_billing_tables():
    Base.metadata.create_all(bind=engine)
    print("UserSubscriptions and UsageRecords tables migration complete!")

if __name__ == "__main__":
    migrate_billing_tables()
