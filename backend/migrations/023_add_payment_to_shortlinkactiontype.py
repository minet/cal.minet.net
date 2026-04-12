import os
import logging
from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")

def run_migration():
    logger.info("Running migration 023: Add 'PAYMENT' to ShortLinkActionType enum")
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        # PostgreSQL doesn't allow ALTER TYPE ... ADD VALUE within a transaction block in some versions/drivers
        # but here we are likely using a simple connection. 
        # We need to use autocommit for this operation.
        conn.execution_options(isolation_level="AUTOCOMMIT")
        
        try:
            # Check if it already exists to be idempotent
            check_sql = text("SELECT 1 FROM pg_enum JOIN pg_type ON pg_enum.enumtypid = pg_type.oid WHERE pg_type.typname = 'shortlinkactiontype' AND enumlabel = 'PAYMENT'")
            exists = conn.execute(check_sql).fetchone()
            
            if not exists:
                logger.info("Adding 'PAYMENT' value to shortlinkactiontype enum...")
                conn.execute(text("ALTER TYPE shortlinkactiontype ADD VALUE 'PAYMENT'"))
                logger.info("Successfully added 'PAYMENT' to enum.")
            else:
                logger.info("'PAYMENT' value already exists in shortlinkactiontype enum.")
                
        except Exception as e:
            logger.error(f"Migration 023 failed: {e}")
            # If the error is that the value already exists, we can ignore it
            if "already exists" in str(e).lower():
                logger.info("Value already exists, ignoring error.")
            else:
                raise e

if __name__ == "__main__":
    run_migration()
