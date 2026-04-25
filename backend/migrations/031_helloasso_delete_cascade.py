"""Migration 031: Add ON DELETE CASCADE to paymentformbilleterie.helloasso_org_id FK.
This fixes the IntegrityError when deleting HelloAsso credentials.
"""

import logging
import os

from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)

DATABASE_URL: str = os.getenv("DATABASE_URL") or ""
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")


def run_migration():
    logger.info("Connecting to database for migration 031...")
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")

        logger.info("Updating paymentformbilleterie_helloasso_org_id_fkey with ON DELETE CASCADE...")
        
        # We need to drop the constraint and recreate it with ON DELETE CASCADE
        conn.execute(
            text(
                """
                ALTER TABLE paymentformbilleterie 
                DROP CONSTRAINT IF EXISTS paymentformbilleterie_helloasso_org_id_fkey;
                
                ALTER TABLE paymentformbilleterie
                ADD CONSTRAINT paymentformbilleterie_helloasso_org_id_fkey
                FOREIGN KEY (helloasso_org_id) 
                REFERENCES organizationhelloasso(id)
                ON DELETE CASCADE;
                """
            )
        )

        logger.info("Migration 031 completed successfully.")
