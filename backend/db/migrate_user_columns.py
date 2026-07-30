import sys
import os
sys.path.insert(0, os.path.abspath("."))

from sqlalchemy import text
from backend.db.database import engine

def migrate_users_table():
    queries = [
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT FALSE;",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_url VARCHAR(500);",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;",
    ]
    with engine.connect() as conn:
        for q in queries:
            try:
                conn.execute(text(q))
                conn.commit()
            except Exception as e:
                print(f"Query note: {q} -> {e}")
    print("Users table schema migration complete!")

if __name__ == "__main__":
    migrate_users_table()
