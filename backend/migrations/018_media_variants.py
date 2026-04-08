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

            # ------------------------------------------------------------------ #
            # 1. Add new columns to storedfile
            # ------------------------------------------------------------------ #
            logger.info(
                "Adding processed, file_type, variants, retry_count columns to storedfile..."
            )
            conn.execute(
                text(
                    """
                ALTER TABLE storedfile
                    ADD COLUMN IF NOT EXISTS processed BOOLEAN NOT NULL DEFAULT FALSE,
                    ADD COLUMN IF NOT EXISTS file_type VARCHAR NOT NULL DEFAULT 'image',
                    ADD COLUMN IF NOT EXISTS variants TEXT,
                    ADD COLUMN IF NOT EXISTS retry_count INTEGER NOT NULL DEFAULT 0;
            """
                )
            )

            # Update file_type for existing video records
            conn.execute(
                text(
                    """
                UPDATE storedfile
                SET file_type = 'video'
                WHERE content_type LIKE 'video/%';
            """
                )
            )

            # ------------------------------------------------------------------ #
            # 2. Add FK columns to entity tables
            # ------------------------------------------------------------------ #
            logger.info("Adding FK columns to entity tables...")

            conn.execute(
                text(
                    """
                ALTER TABLE "user"
                    ADD COLUMN IF NOT EXISTS profile_picture_file_id UUID
                    REFERENCES storedfile(id);
            """
                )
            )

            conn.execute(
                text(
                    """
                ALTER TABLE organization
                    ADD COLUMN IF NOT EXISTS logo_file_id UUID
                    REFERENCES storedfile(id);
            """
                )
            )

            conn.execute(
                text(
                    """
                ALTER TABLE organizationimage
                    ADD COLUMN IF NOT EXISTS stored_file_id UUID
                    REFERENCES storedfile(id);
            """
                )
            )

            conn.execute(
                text(
                    """
                ALTER TABLE event
                    ADD COLUMN IF NOT EXISTS poster_file_id UUID
                    REFERENCES storedfile(id),
                    ADD COLUMN IF NOT EXISTS video_file_id UUID
                    REFERENCES storedfile(id);
            """
                )
            )

            # ------------------------------------------------------------------ #
            # 3. Backfill helper: ensure a storedfile row exists for a given URL
            #    and return its id. We use a temporary PL/pgSQL function.
            # ------------------------------------------------------------------ #
            logger.info("Creating helper function for backfill...")
            conn.execute(
                text(
                    """
                CREATE OR REPLACE FUNCTION _ensure_storedfile(p_url TEXT)
                RETURNS UUID
                LANGUAGE plpgsql AS $$
                DECLARE
                    v_stored_filename TEXT;
                    v_id UUID;
                    v_content_type TEXT;
                    v_ext TEXT;
                BEGIN
                    IF p_url IS NULL OR p_url = '' THEN
                        RETURN NULL;
                    END IF;

                    -- Strip /uploads/ prefix to get stored_filename
                    v_stored_filename := regexp_replace(p_url, '^/uploads/', '');

                    -- Check existing row
                    SELECT id INTO v_id
                    FROM storedfile
                    WHERE stored_filename = v_stored_filename
                    LIMIT 1;

                    IF v_id IS NOT NULL THEN
                        RETURN v_id;
                    END IF;

                    -- Guess content_type from extension
                    v_ext := lower(regexp_replace(v_stored_filename, '^.*\\.', ''));
                    v_content_type := CASE v_ext
                        WHEN 'jpg'  THEN 'image/jpeg'
                        WHEN 'jpeg' THEN 'image/jpeg'
                        WHEN 'png'  THEN 'image/png'
                        WHEN 'gif'  THEN 'image/gif'
                        WHEN 'webp' THEN 'image/webp'
                        WHEN 'svg'  THEN 'image/svg+xml'
                        WHEN 'mp4'  THEN 'video/mp4'
                        WHEN 'webm' THEN 'video/webm'
                        WHEN 'mov'  THEN 'video/quicktime'
                        WHEN 'avi'  THEN 'video/x-msvideo'
                        WHEN 'mkv'  THEN 'video/x-matroska'
                        ELSE 'application/octet-stream'
                    END;

                    v_id := gen_random_uuid();

                    INSERT INTO storedfile (
                        id, stored_filename, original_filename, url,
                        content_type, size, uploaded_by_id, uploaded_at,
                        processed, file_type, variants, retry_count
                    ) VALUES (
                        v_id,
                        v_stored_filename,
                        v_stored_filename,
                        p_url,
                        v_content_type,
                        0,
                        '00000000-0000-4000-8000-000000000001',
                        NOW(),
                        TRUE,
                        CASE WHEN v_content_type LIKE 'video/%' THEN 'video' ELSE 'image' END,
                        '[]',
                        0
                    );

                    RETURN v_id;
                END;
                $$;
            """
                )
            )

            # ------------------------------------------------------------------ #
            # 4. Backfill FK columns from existing URL columns
            # ------------------------------------------------------------------ #
            logger.info("Backfilling user.profile_picture_file_id...")
            conn.execute(
                text(
                    """
                UPDATE "user"
                SET profile_picture_file_id = _ensure_storedfile(profile_picture_url)
                WHERE profile_picture_url IS NOT NULL
                  AND profile_picture_url != ''
                  AND profile_picture_file_id IS NULL;
            """
                )
            )

            logger.info("Backfilling organization.logo_file_id...")
            conn.execute(
                text(
                    """
                UPDATE organization
                SET logo_file_id = _ensure_storedfile(logo_url)
                WHERE logo_url IS NOT NULL
                  AND logo_url != ''
                  AND logo_file_id IS NULL;
            """
                )
            )

            logger.info("Backfilling organizationimage.stored_file_id...")
            conn.execute(
                text(
                    """
                UPDATE organizationimage
                SET stored_file_id = _ensure_storedfile(url)
                WHERE url IS NOT NULL
                  AND url != ''
                  AND stored_file_id IS NULL;
            """
                )
            )

            logger.info("Backfilling event.poster_file_id...")
            conn.execute(
                text(
                    """
                UPDATE event
                SET poster_file_id = _ensure_storedfile(poster_url)
                WHERE poster_url IS NOT NULL
                  AND poster_url != ''
                  AND poster_file_id IS NULL;
            """
                )
            )

            logger.info("Backfilling event.video_file_id...")
            conn.execute(
                text(
                    """
                UPDATE event
                SET video_file_id = _ensure_storedfile(video_url)
                WHERE video_url IS NOT NULL
                  AND video_url != ''
                  AND video_file_id IS NULL;
            """
                )
            )

            # Clean up helper function
            conn.execute(text("DROP FUNCTION IF EXISTS _ensure_storedfile(TEXT);"))

            # Drop old URL columns if desired
            logger.info("Dropping old URL columns...")
            conn.execute(
                text(
                    """
                ALTER TABLE "user" DROP COLUMN IF EXISTS profile_picture_url;
            """
                )
            )
            conn.execute(
                text(
                    """
                ALTER TABLE organization DROP COLUMN IF EXISTS logo_url;
            """
                )
            )
            conn.execute(
                text(
                    """
                ALTER TABLE organizationimage DROP COLUMN IF EXISTS url;
            """
                )
            )
            conn.execute(
                text(
                    """
                ALTER TABLE event DROP COLUMN IF EXISTS poster_url;
            """
                )
            )
            conn.execute(
                text(
                    """
                ALTER TABLE event DROP COLUMN IF EXISTS video_url;
            """
                )
            )

            logger.info("Migration 018 completed successfully.")
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise e


if __name__ == "__main__":
    run_migration()
