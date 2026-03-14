import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/calendint")

def run_migration():
    print(f"Connecting to {DATABASE_URL}...")
    try:
        engine = create_engine(DATABASE_URL)
        with engine.begin() as conn:
            print("Adding delete_after to organization...")
            conn.execute(text("""
                ALTER TABLE organization 
                ADD COLUMN IF NOT EXISTS delete_after TIMESTAMP WITH TIME ZONE;
            """))
            print("Migration 011 completed successfully.")
    except Exception as e:
        print(f"Migration failed: {e}")
        raise e

if __name__ == "__main__":
    run_migration()
