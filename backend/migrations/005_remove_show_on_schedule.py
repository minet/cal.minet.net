import os

from sqlalchemy import create_engine, text
import logging

logger = logging.getLogger(__name__)
# Default to the one in database.py, but allow env override
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
            conn.execution_options(isolation_level="AUTOCOMMIT")

            # Check if column exists
            check_sql = text(
                """
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='event' AND column_name='show_on_schedule';
            """
            )
            result = conn.execute(check_sql).fetchone()

            if result:
                logger.info("Removing show_on_schedule column from event table...")
                alter_sql = text('ALTER TABLE "event" DROP COLUMN show_on_schedule')
                conn.execute(alter_sql)
                logger.info("Migration successful.")
            else:
                logger.info("Column show_on_schedule does not exist.")

    except Exception as e:
        logger.error(f"Migration failed: {e}")


if __name__ == "__main__":
    run_migration()
