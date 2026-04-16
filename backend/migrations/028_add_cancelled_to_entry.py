"""Migration 028: Add cancelled / cancelled_at columns to eventpaymententry."""

import logging
import os

from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)

DATABASE_URL: str = os.getenv("DATABASE_URL") or ""
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")


def run_migration():
    logger.info("Connecting to database for migration 028...")
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")

        logger.info("Adding cancelled column...")
        conn.execute(text(
            "ALTER TABLE eventpaymententry ADD COLUMN IF NOT EXISTS "
            "cancelled BOOLEAN NOT NULL DEFAULT FALSE;"
        ))

        logger.info("Adding cancelled_at column...")
        conn.execute(text(
            "ALTER TABLE eventpaymententry ADD COLUMN IF NOT EXISTS cancelled_at TIMESTAMPTZ;"
        ))

        logger.info("Migration 028 completed successfully.")
