"""Migration 030: Add changelog system (changelogentry table + user.last_seen_changelog_id)."""

import logging
import os

from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)

DATABASE_URL: str = os.getenv("DATABASE_URL") or ""
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")


def run_migration():
    logger.info("Connecting to database for migration 030...")
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")

        logger.info("Creating changelogentry table...")
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS changelogentry (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    title VARCHAR NOT NULL,
                    content TEXT NOT NULL,
                    audience VARCHAR NOT NULL DEFAULT 'all',
                    image_urls TEXT,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
                );
                """
            )
        )

        logger.info("Adding index on changelogentry.created_at...")
        conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_changelogentry_created_at "
                "ON changelogentry (created_at);"
            )
        )

        logger.info("Adding last_seen_changelog_id to user table...")
        conn.execute(
            text(
                "ALTER TABLE \"user\" ADD COLUMN IF NOT EXISTS "
                "last_seen_changelog_id UUID REFERENCES changelogentry(id);"
            )
        )

        logger.info("Migration 030 completed successfully.")
