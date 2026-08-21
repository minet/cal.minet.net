"""Migration 032: Add created_at to membership table (for mandate-reminder tracking)."""

import logging
import os

from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)

DATABASE_URL: str = os.getenv("DATABASE_URL") or ""
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")


def run_migration():
    logger.info("Connecting to database for migration 032...")
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")

        logger.info("Adding created_at to membership table...")
        conn.execute(
            text(
                "ALTER TABLE membership ADD COLUMN IF NOT EXISTS "
                "created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now();"
            )
        )

        logger.info("Migration 032 completed successfully.")
