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
            conn.execution_options(isolation_level="AUTOCOMMIT")

            logger.info("Adding title column to membership...")
            conn.execute(
                text("ALTER TABLE membership ADD COLUMN IF NOT EXISTS title VARCHAR")
            )

            logger.info("Migration successful.")

    except Exception as e:
        logger.error(f"Migration failed: {e}")


if __name__ == "__main__":
    run_migration()
