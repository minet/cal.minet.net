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
            logger.info("Creating organizationimage table...")
            conn.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS organizationimage (
                    id UUID PRIMARY KEY,
                    organization_id UUID NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
                    url VARCHAR NOT NULL,
                    filename VARCHAR NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            """
                )
            )
            logger.info("Migration 013 completed successfully.")
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise e


if __name__ == "__main__":
    run_migration()
