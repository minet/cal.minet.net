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

            # Check if table exists
            check_sql = text(
                """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name='shortlink';
            """
            )
            result = conn.execute(check_sql).fetchone()

            if not result:
                logger.info("Creating shortlink table...")
                create_sql = text(
                    """
                CREATE TABLE IF NOT EXISTS shortlink (
                    id VARCHAR PRIMARY KEY,
                    item_type VARCHAR NOT NULL,
                    action_type VARCHAR NOT NULL,
                    item_id UUID NOT NULL,
                    created_by_id UUID NOT NULL,
                    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (now() at time zone 'utc'),
                    last_used_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (now() at time zone 'utc'),
                    FOREIGN KEY (created_by_id) REFERENCES "user" (id)
                );
                """
                )
                conn.execute(create_sql)
                logger.info("Migration successful.")
            else:
                logger.info("Table shortlink already exists.")

    except Exception as e:
        logger.error(f"Migration failed: {e}")


if __name__ == "__main__":
    run_migration()
