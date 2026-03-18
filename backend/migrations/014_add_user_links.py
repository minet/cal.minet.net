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

            print("Creating userlink table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS userlink (
                    id UUID PRIMARY KEY,
                    user_id UUID NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
                    name VARCHAR NOT NULL,
                    url VARCHAR NOT NULL,
                    "order" INTEGER NOT NULL DEFAULT 0
                );
            """))

            print("Migrating existing facebook_links to userlink...")
            conn.execute(text("""
                INSERT INTO userlink (id, user_id, name, url, "order")
                SELECT gen_random_uuid(), id, 'Facebook', facebook_link, 0
                FROM "user"
                WHERE facebook_link IS NOT NULL AND facebook_link != '';
            """))

            print("Dropping facebook_link column from user table...")
            conn.execute(text("""
                ALTER TABLE "user" DROP COLUMN IF EXISTS facebook_link;
            """))

            print("Migration 014 completed successfully.")
    except Exception as e:
        print(f"Migration failed: {e}")
        raise e

if __name__ == "__main__":
    run_migration()
