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
            logger.info("Adding Ghost user...")
            conn.execute(
                text(
                    """
                INSERT INTO "user" (id, email, full_name, is_active, is_superadmin, notification_delay)
                VALUES ('00000000-0000-4000-8000-000000000001', 'ghost-user@calendint.local', 'Utilisateur Fantôme', false, false, -1)
                ON CONFLICT (id) DO NOTHING;
            """
                )
            )

            logger.info("Adding Ghost organization...")
            conn.execute(
                text(
                    """
                INSERT INTO organization (id, name, slug, description, type, created_at, updated_at)
                VALUES (
                    '00000000-0000-4000-8000-000000000002', 
                    'Organisation Fantôme', 
                    'ghost-org', 
                    'Organisation utilisée pour les entités supprimées ou orphelines.',
                    'ADMINISTRATION',
                    now(),
                    now()
                )
                ON CONFLICT (id) DO NOTHING;
            """
                )
            )
            logger.info("Migration 010 completed successfully.")
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise e


if __name__ == "__main__":
    run_migration()
