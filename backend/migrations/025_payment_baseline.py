"""Migration 025: Add baseline counters to eventpaymentform for user deletion RGPD.

When a user account is removed (housekeeping), their completed EventPaymentEntry
records are aggregated into these two columns before the entries are deleted,
so the payment form retains accurate revenue and headcount totals.
"""

import logging
import os

from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)

DATABASE_URL: str = os.getenv("DATABASE_URL") or ""
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")


def run_migration():
    logger.info("Connecting to database for migration 025...")
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")

        logger.info("Adding baseline columns to eventpaymentform...")
        conn.execute(
            text(
                """
                ALTER TABLE eventpaymentform
                    ADD COLUMN IF NOT EXISTS baseline_total_amount_cents INTEGER NOT NULL DEFAULT 0,
                    ADD COLUMN IF NOT EXISTS baseline_participant_count  INTEGER NOT NULL DEFAULT 0;
                """
            )
        )

        logger.info("Migration 025 completed successfully.")
