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

            # Check if table exists
            check_sql = text(
                """
                SELECT to_regclass('public.ldapuser');
            """
            )
            result = conn.execute(check_sql).fetchone()

            if not result or not result[0]:
                logger.info("Creating table ldapuser...")
                create_sql = text(
                    """
                CREATE TABLE ldapuser (
                    id UUID NOT NULL, 
                    email VARCHAR NOT NULL, 
                    full_name VARCHAR, 
                    uid VARCHAR, 
                    synced_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
                    PRIMARY KEY (id)
                );
                CREATE UNIQUE INDEX ix_ldapuser_email ON ldapuser (email);
                CREATE INDEX ix_ldapuser_uid ON ldapuser (uid);
                """
                )
                conn.execute(create_sql)
                logger.info("Migration successful.")
            else:
                logger.info("Table ldapuser already exists.")

    except Exception as e:
        logger.error(f"Migration failed: {e}")


if __name__ == "__main__":
    run_migration()
