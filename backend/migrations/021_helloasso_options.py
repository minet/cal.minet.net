"""Migration 021: Add payment form options, open/close flag, and per-user payment entries.

- eventpaymentform.options: JSON list of add-on options
- eventpaymentform.is_open: whether new payments can be initiated
- eventpaymententry: tracks per-user checkout initiations and completions
"""

import logging
import os

from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)

DATABASE_URL: str = os.getenv("DATABASE_URL") or ""
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")


def run_migration():
    logger.info("Connecting to database for migration 021...")
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")

        # ------------------------------------------------------------------
        # 1. New columns on eventpaymentform
        # ------------------------------------------------------------------
        logger.info("Adding options and is_open columns to eventpaymentform...")
        conn.execute(text(
            "ALTER TABLE eventpaymentform ADD COLUMN IF NOT EXISTS options TEXT;"
        ))
        conn.execute(text(
            "ALTER TABLE eventpaymentform ADD COLUMN IF NOT EXISTS is_open BOOLEAN NOT NULL DEFAULT TRUE;"
        ))

        # ------------------------------------------------------------------
        # 2. Per-user payment entry table
        # ------------------------------------------------------------------
        logger.info("Creating eventpaymententry table...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS eventpaymententry (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                payment_form_id UUID NOT NULL
                    REFERENCES eventpaymentform(id) ON DELETE CASCADE,
                user_id UUID NOT NULL REFERENCES "user"(id),
                checkout_intent_id TEXT NOT NULL UNIQUE,
                completed BOOLEAN NOT NULL DEFAULT FALSE,
                completed_at TIMESTAMPTZ,
                selected_option_indices TEXT,
                amount_cents INTEGER NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now()
            );
        """))
        conn.execute(text(
            "CREATE INDEX IF NOT EXISTS ix_eventpaymententry_payment_form_id "
            "ON eventpaymententry(payment_form_id);"
        ))
        conn.execute(text(
            "CREATE INDEX IF NOT EXISTS ix_eventpaymententry_checkout_intent_id "
            "ON eventpaymententry(checkout_intent_id);"
        ))

        logger.info("Migration 021 completed successfully.")
