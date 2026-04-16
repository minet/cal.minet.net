"""Migration 022: Add payment_type, validation fields, manual entry support to eventpaymententry."""

import logging
import os

from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)

DATABASE_URL: str = os.getenv("DATABASE_URL") or ""
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")


def run_migration():
    logger.info("Connecting to database for migration 022...")
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")

        logger.info("Making user_id and checkout_intent_id nullable for manual entries...")
        conn.execute(text(
            "ALTER TABLE eventpaymententry ALTER COLUMN user_id DROP NOT NULL;"
        ))
        conn.execute(text(
            "ALTER TABLE eventpaymententry ALTER COLUMN checkout_intent_id DROP NOT NULL;"
        ))

        logger.info("Adding payment_type column...")
        conn.execute(text(
            "ALTER TABLE eventpaymententry ADD COLUMN IF NOT EXISTS "
            "payment_type TEXT NOT NULL DEFAULT 'helloasso';"
        ))

        logger.info("Adding attendee_name column for manual entries...")
        conn.execute(text(
            "ALTER TABLE eventpaymententry ADD COLUMN IF NOT EXISTS attendee_name TEXT;"
        ))

        logger.info("Adding validation columns...")
        conn.execute(text(
            "ALTER TABLE eventpaymententry ADD COLUMN IF NOT EXISTS "
            "validated BOOLEAN NOT NULL DEFAULT FALSE;"
        ))
        conn.execute(text(
            "ALTER TABLE eventpaymententry ADD COLUMN IF NOT EXISTS validated_at TIMESTAMPTZ;"
        ))
        conn.execute(text(
            'ALTER TABLE eventpaymententry ADD COLUMN IF NOT EXISTS '
            'validated_by_id UUID REFERENCES "user"(id);'
        ))

        logger.info("Migration 022 completed successfully.")
