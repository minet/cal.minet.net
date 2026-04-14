"""Migration 026: Add imported_options column to eventpaymententry.

Stores a JSON list of {"name": str, "amount_cents": int} objects captured
from HelloAsso billeterie items (withDetails=true) at import time.
"""

import logging
import os

from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)

DATABASE_URL: str = os.getenv("DATABASE_URL") or ""
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")


def run_migration():
    logger.info("Connecting to database for migration 026...")
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")

        logger.info("Adding imported_options column to eventpaymententry...")
        conn.execute(
            text(
                """
                ALTER TABLE eventpaymententry
                    ADD COLUMN IF NOT EXISTS imported_options TEXT;
                """
            )
        )

        logger.info("Migration 026 completed successfully.")
