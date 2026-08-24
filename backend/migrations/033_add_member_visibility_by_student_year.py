"""Migration 033: Add organization-member visibility controls by student year."""

import logging
import os

from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)

DATABASE_URL: str = os.getenv("DATABASE_URL") or ""
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")


def run_migration():
    logger.info("Connecting to database for migration 033...")
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")

        for year in (1, 2, 3):
            conn.execute(
                text(
                    "ALTER TABLE organization ADD COLUMN IF NOT EXISTS "
                    f"hide_members_from_year_{year} BOOLEAN NOT NULL DEFAULT FALSE;"
                )
            )
            conn.execute(
                text(
                    "ALTER TABLE membership ADD COLUMN IF NOT EXISTS "
                    f"hide_from_year_{year} BOOLEAN NOT NULL DEFAULT FALSE;"
                )
            )

        conn.execute(
            text("ALTER TABLE ldapuser ADD COLUMN IF NOT EXISTS student_year INTEGER;")
        )
        conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_ldapuser_student_year "
                "ON ldapuser (student_year);"
            )
        )

    logger.info("Migration 033 completed successfully.")


if __name__ == "__main__":
    run_migration()
