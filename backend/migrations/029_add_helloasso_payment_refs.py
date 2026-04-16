"""Migration 029: Add HelloAsso payment and order identifiers to eventpaymententry."""

import logging
import os

from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)

DATABASE_URL: str = os.getenv("DATABASE_URL") or ""
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")


def run_migration():
    logger.info("Connecting to database for migration 029...")
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")

        logger.info("Adding helloasso_payment_id column...")
        conn.execute(
            text(
                "ALTER TABLE eventpaymententry ADD COLUMN IF NOT EXISTS "
                "helloasso_payment_id VARCHAR;"
            )
        )

        logger.info("Adding helloasso_order_id column...")
        conn.execute(
            text(
                "ALTER TABLE eventpaymententry ADD COLUMN IF NOT EXISTS "
                "helloasso_order_id VARCHAR;"
            )
        )

        logger.info("Adding index on helloasso_payment_id...")
        conn.execute(
            text(
                "CREATE UNIQUE INDEX IF NOT EXISTS "
                "ix_eventpaymententry_helloasso_payment_id "
                "ON eventpaymententry (helloasso_payment_id);"
            )
        )

        logger.info("Adding index on helloasso_order_id...")
        conn.execute(
            text(
                "CREATE UNIQUE INDEX IF NOT EXISTS "
                "ix_eventpaymententry_helloasso_order_id "
                "ON eventpaymententry (helloasso_order_id);"
            )
        )

        logger.info("Migration 029 completed successfully.")
