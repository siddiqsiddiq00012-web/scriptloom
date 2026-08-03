import sys
import os
sys.path.insert(0, os.path.abspath("."))

from backend.db.database import engine
from backend.models.base import Base
from backend.models.audit_log import AuditLog

def migrate_audit_log_table():
    Base.metadata.create_all(bind=engine)
    print("AuditLog table migration complete!")

if __name__ == "__main__":
    migrate_audit_log_table()
