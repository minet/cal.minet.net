import os
from sqlalchemy import create_engine, text
import logging

logger = logging.getLogger(__name__)

DATABASE_URL: str = os.getenv("DATABASE_URL") or ""
if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL is not set, please set it in the environment variables."
    )


def run_migration():
    logger.info(f"Connecting to {DATABASE_URL}...")
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            conn.execution_options(isolation_level="AUTOCOMMIT")

            logger.info("Adding sequence column to event table...")
            conn.execute(
                text(
                    """
                ALTER TABLE event ADD COLUMN IF NOT EXISTS sequence INTEGER NOT NULL DEFAULT 0;
            """
                )
            )

            logger.info("Setting sequence to 1 for existing events...")
            conn.execute(
                text(
                    """
                UPDATE event SET sequence = 1;
            """
                )
            )

            # Force an update for all the existing events to set the updated_at timestamp
            logger.info("Adding updated_at column to event table...")
            conn.execute(
                text(
                    """
                ALTER TABLE event ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE;
            """
                )
            )

            logger.info("Setting updated_at timestamp for existing events...")
            conn.execute(
                text(
                    """
                UPDATE event SET updated_at = NOW();
            """
                )
            )

            logger.info("Migration 017 completed successfully.")
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise e


if __name__ == "__main__":
    run_migration()
