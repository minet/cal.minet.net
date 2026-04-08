import os
from sqlalchemy import create_engine, text
import logging

logger = logging.getLogger(__name__)
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    raise ValueError(
        "DATABASE_URL is not set, please set it in the environment variables."
    )


def run_migration():
    logger.info(f"Connecting to {DATABASE_URL}...")
    try:
        if DATABASE_URL is None:
            raise ValueError(
                "DATABASE_URL is not set, please set it in the environment variables."
            )

        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            logger.info("Adding exempt_from_rgpd_delete to user...")
            conn.execute(
                text(
                    """
                ALTER TABLE "user" 
                ADD COLUMN IF NOT EXISTS exempt_from_rgpd_delete BOOLEAN NOT NULL DEFAULT FALSE;
            """
                )
            )
            logger.info("Migration 012 completed successfully.")
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise e


if __name__ == "__main__":
    run_migration()
