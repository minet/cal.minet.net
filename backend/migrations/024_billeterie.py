"""Migration 024: Add paymentformbilleterie table and fix EventPaymentForm org FK handling.

- paymentformbilleterie: links a payment form to a HelloAsso billeterie for attendee import.
  FK to eventpaymentform ON DELETE CASCADE.
  FK to organizationhelloasso ON DELETE CASCADE (auto-cleanup when HA integration removed).
"""

import logging
import os

from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)

DATABASE_URL: str = os.getenv("DATABASE_URL") or ""
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")


def run_migration():
    logger.info("Connecting to database for migration 024...")
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")

        # ------------------------------------------------------------------
        # 1. paymentformbilleterie table
        # ------------------------------------------------------------------
        logger.info("Creating paymentformbilleterie table...")
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS paymentformbilleterie (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    payment_form_id UUID NOT NULL UNIQUE
                        REFERENCES eventpaymentform(id) ON DELETE CASCADE,
                    helloasso_org_id UUID NOT NULL
                        REFERENCES organizationhelloasso(id) ON DELETE CASCADE,
                    helloasso_form_slug TEXT NOT NULL,
                    helloasso_form_title TEXT NOT NULL,
                    helloasso_form_type TEXT NOT NULL DEFAULT 'Event',
                    last_imported_at TIMESTAMPTZ,
                    created_by_id UUID NOT NULL REFERENCES "user"(id),
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
                );
                """
            )
        )

        # ------------------------------------------------------------------
        # 2. Fix eventpaymentform.approving_org_id FK to allow SET NULL on
        #    org deletion (drop the existing FK, re-add with ON DELETE SET NULL).
        # ------------------------------------------------------------------
        logger.info("Fixing eventpaymentform.approving_org_id FK to ON DELETE SET NULL...")
        # Drop the existing unnamed FK constraint (PostgreSQL names it automatically)
        conn.execute(
            text(
                """
                DO $$
                DECLARE
                    c TEXT;
                BEGIN
                    SELECT conname INTO c
                    FROM pg_constraint
                    WHERE conrelid = 'eventpaymentform'::regclass
                      AND contype = 'f'
                      AND conkey = ARRAY[
                          (SELECT attnum FROM pg_attribute
                           WHERE attrelid = 'eventpaymentform'::regclass
                             AND attname = 'approving_org_id')
                      ]::smallint[];
                    IF c IS NOT NULL THEN
                        EXECUTE 'ALTER TABLE eventpaymentform DROP CONSTRAINT ' || quote_ident(c);
                    END IF;
                END
                $$;
                """
            )
        )
        conn.execute(
            text(
                """
                ALTER TABLE eventpaymentform
                    ADD CONSTRAINT eventpaymentform_approving_org_id_fkey
                    FOREIGN KEY (approving_org_id)
                    REFERENCES organization(id)
                    ON DELETE SET NULL;
                """
            )
        )

        logger.info("Migration 024 completed successfully.")
