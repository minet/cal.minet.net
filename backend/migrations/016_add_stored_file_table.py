import os
from sqlalchemy import create_engine, text

DATABASE_URL: str = os.getenv("DATABASE_URL") or ""
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set, please set it in the environment variables.")

def run_migration():
    print(f"Connecting to {DATABASE_URL}...")
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            conn.execution_options(isolation_level="AUTOCOMMIT")

            print("Creating storedfile table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS storedfile (
                    id UUID PRIMARY KEY,
                    stored_filename VARCHAR NOT NULL,
                    original_filename VARCHAR NOT NULL,
                    url VARCHAR NOT NULL,
                    content_type VARCHAR NOT NULL,
                    size INTEGER NOT NULL,
                    uploaded_by_id UUID NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
                    uploaded_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
                );
            """))

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_storedfile_stored_filename
                    ON storedfile (stored_filename);
            """))

            print("Migration 016 completed successfully.")
    except Exception as e:
        print(f"Migration failed: {e}")
        raise e

if __name__ == "__main__":
    run_migration()
