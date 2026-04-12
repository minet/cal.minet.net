"""Migration 020: Add HelloAsso payment integration tables.

- organizationhelloasso: stores per-org encrypted API credentials (client_id + client_secret)
- eventpaymentform: tracks payment form proposals + approval state
- membership.can_manage_payment_forms: new permission flag
"""

import logging
import os

from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)

DATABASE_URL: str = os.getenv("DATABASE_URL") or ""
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")


def run_migration():
    logger.info("Connecting to database for migration 020...")
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")

        # ------------------------------------------------------------------
        # 1. OrganizationHelloAsso — stores encrypted API key pair per org
        # ------------------------------------------------------------------
        logger.info("Creating organizationhelloasso table...")
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS organizationhelloasso (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    organization_id UUID NOT NULL UNIQUE
                        REFERENCES organization(id) ON DELETE CASCADE,
                    helloasso_slug TEXT NOT NULL,
                    api_client_id TEXT NOT NULL,
                    api_client_secret TEXT NOT NULL,
                    cached_access_token TEXT,
                    token_expires_at TIMESTAMPTZ,
                    connected_by_id UUID NOT NULL REFERENCES "user"(id),
                    connected_at TIMESTAMPTZ NOT NULL DEFAULT now()
                );
            """
            )
        )

        # ------------------------------------------------------------------
        # 2. PaymentFormStatus enum
        # ------------------------------------------------------------------
        logger.info("Creating paymentformstatus enum...")
        conn.execute(
            text(
                """
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_type WHERE typname = 'paymentformstatus'
                    ) THEN
                        CREATE TYPE paymentformstatus AS ENUM ('pending', 'approved', 'rejected');
                    END IF;
                END
                $$;
            """
            )
        )

        # ------------------------------------------------------------------
        # 3. EventPaymentForm — proposal + checkout state
        # ------------------------------------------------------------------
        logger.info("Creating eventpaymentform table...")
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS eventpaymentform (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    event_id UUID NOT NULL UNIQUE REFERENCES event(id) ON DELETE CASCADE,
                    requesting_org_id UUID NOT NULL REFERENCES organization(id),
                    approving_org_id UUID REFERENCES organization(id),
                    total_amount_cents INTEGER NOT NULL,
                    item_name TEXT NOT NULL,
                    status paymentformstatus NOT NULL DEFAULT 'pending',
                    last_checkout_intent_id TEXT,
                    rejection_message TEXT,
                    payment_completed BOOLEAN NOT NULL DEFAULT FALSE,
                    created_by_id UUID NOT NULL REFERENCES "user"(id),
                    reviewed_by_id UUID REFERENCES "user"(id),
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                    reviewed_at TIMESTAMPTZ
                );
            """
            )
        )

        # ------------------------------------------------------------------
        # 4. Membership permission flag
        # ------------------------------------------------------------------
        logger.info("Adding can_manage_payment_forms column to membership...")
        conn.execute(
            text(
                """
                ALTER TABLE membership
                    ADD COLUMN IF NOT EXISTS can_manage_payment_forms
                    BOOLEAN NOT NULL DEFAULT FALSE;
            """
            )
        )

        logger.info("Migration 020 completed successfully.")
