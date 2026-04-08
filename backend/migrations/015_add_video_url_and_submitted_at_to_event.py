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

            logger.info("Adding video_url column to event table...")
            conn.execute(
                text(
                    """
                ALTER TABLE event ADD COLUMN IF NOT EXISTS video_url VARCHAR;
            """
                )
            )

            logger.info("Adding submitted_at column to event table...")
            conn.execute(
                text(
                    """
                ALTER TABLE event ADD COLUMN IF NOT EXISTS submitted_at TIMESTAMP WITH TIME ZONE;
            """
                )
            )

            logger.info(
                "Backfilling submitted_at from created_at for PUBLIC_PENDING events..."
            )
            conn.execute(
                text(
                    """
                UPDATE event SET submitted_at = created_at
                WHERE visibility::text = 'public_pending' AND submitted_at IS NULL;
            """
                )
            )

            logger.info("Migration 015 completed successfully.")
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise e


if __name__ == "__main__":
    run_migration()
