import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/calendint")

def run_migration():
    print(f"Connecting to {DATABASE_URL}...")
    try:
        engine = create_engine(DATABASE_URL)
        with engine.begin() as conn:
            print("Adding exempt_from_rgpd_delete to user...")
            conn.execute(text("""
                ALTER TABLE "user" 
                ADD COLUMN IF NOT EXISTS exempt_from_rgpd_delete BOOLEAN NOT NULL DEFAULT FALSE;
            """))
            print("Migration 012 completed successfully.")
    except Exception as e:
        print(f"Migration failed: {e}")
        raise e

if __name__ == "__main__":
    run_migration()
