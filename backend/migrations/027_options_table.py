"""Migration 027: Normalize payment form options into dedicated tables.

- Create eventpaymentformoption and eventpaymentformoptionuser tables.
- Migrate eventpaymentform.options JSON rows into eventpaymentformoption rows.
- Convert eventpaymententry.selected_option_indices (int list) into UUID list.
- Rename selected_option_indices -> selected_option_ids.
- Drop legacy eventpaymentform.options column.
"""

import json
import logging
import os
from uuid import UUID
from uuid import uuid4

from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)

DATABASE_URL: str = os.getenv("DATABASE_URL") or ""
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")


def _has_column(conn, table_name: str, column_name: str) -> bool:
    row = conn.execute(
        text(
            """
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = :table_name
              AND column_name = :column_name
            LIMIT 1;
            """
        ),
        {"table_name": table_name, "column_name": column_name},
    ).first()
    return row is not None


def run_migration():
    logger.info("Connecting to database for migration 027...")
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")

        logger.info("Creating eventpaymentformoption table...")
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS eventpaymentformoption (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    payment_form_id UUID NOT NULL
                        REFERENCES eventpaymentform(id) ON DELETE CASCADE,
                    name TEXT NOT NULL,
                    price_cents INTEGER NOT NULL,
                    is_private BOOLEAN NOT NULL DEFAULT FALSE,
                    "order" INTEGER NOT NULL DEFAULT 0
                );
                """
            )
        )
        conn.execute(
            text(
                """
                CREATE INDEX IF NOT EXISTS ix_eventpaymentformoption_payment_form_id
                ON eventpaymentformoption(payment_form_id);
                """
            )
        )

        logger.info("Creating eventpaymentformoptionuser table...")
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS eventpaymentformoptionuser (
                    option_id UUID NOT NULL
                        REFERENCES eventpaymentformoption(id) ON DELETE CASCADE,
                    user_id UUID NOT NULL
                        REFERENCES "user"(id) ON DELETE CASCADE,
                    PRIMARY KEY (option_id, user_id)
                );
                """
            )
        )

        has_form_options = _has_column(conn, "eventpaymentform", "options")
        has_entry_indices = _has_column(
            conn, "eventpaymententry", "selected_option_indices"
        )
        has_entry_ids = _has_column(conn, "eventpaymententry", "selected_option_ids")

        form_index_to_option_ids: dict[str, dict[int, str]] = {}

        if has_form_options:
            logger.info("Migrating eventpaymentform.options JSON to option tables...")
            # Retry safety: if migration previously failed mid-run, restart from a clean state.
            conn.execute(text("DELETE FROM eventpaymentformoptionuser;"))
            conn.execute(text("DELETE FROM eventpaymentformoption;"))
            forms = conn.execute(
                text(
                    """
                    SELECT id, options
                    FROM eventpaymentform
                    WHERE options IS NOT NULL
                      AND btrim(options) <> '';
                    """
                )
            ).all()

            for form_id, raw_options in forms:
                try:
                    data = json.loads(raw_options)
                except Exception:
                    continue
                if not isinstance(data, list):
                    continue

                index_map: dict[int, str] = {}
                for idx, item in enumerate(data):
                    if not isinstance(item, dict):
                        continue

                    name = str(item.get("name") or "").strip()
                    if not name:
                        continue

                    try:
                        price_cents = int(item.get("price_cents", 0))
                    except Exception:
                        price_cents = 0
                    is_private = bool(item.get("is_private", False))

                    option_id = uuid4()
                    conn.execute(
                        text(
                            """
                            INSERT INTO eventpaymentformoption
                                (id, payment_form_id, name, price_cents, is_private, "order")
                            VALUES
                                (:id, :payment_form_id, :name, :price_cents, :is_private, :order);
                            """
                        ),
                        {
                            "id": option_id,
                            "payment_form_id": form_id,
                            "name": name,
                            "price_cents": price_cents,
                            "is_private": is_private,
                            "order": idx,
                        },
                    )

                    index_map[idx] = str(option_id)

                    allowed_user_ids = item.get("allowed_user_ids") or []
                    if isinstance(allowed_user_ids, list):
                        for uid in allowed_user_ids:
                            try:
                                user_id = UUID(str(uid))
                            except Exception:
                                continue
                            conn.execute(
                                text(
                                    """
                                    INSERT INTO eventpaymentformoptionuser (option_id, user_id)
                                    VALUES (:option_id, :user_id)
                                    ON CONFLICT DO NOTHING;
                                    """
                                ),
                                {"option_id": option_id, "user_id": user_id},
                            )

                if index_map:
                    form_index_to_option_ids[str(form_id)] = index_map

        if has_entry_indices:
            logger.info("Converting selected_option_indices to UUID lists...")
            entries = conn.execute(
                text(
                    """
                    SELECT id, payment_form_id, selected_option_indices
                    FROM eventpaymententry
                    WHERE selected_option_indices IS NOT NULL
                      AND btrim(selected_option_indices) <> '';
                    """
                )
            ).all()

            for entry_id, payment_form_id, raw_indices in entries:
                try:
                    indices = json.loads(raw_indices)
                except Exception:
                    continue
                if not isinstance(indices, list):
                    continue

                mapping = form_index_to_option_ids.get(str(payment_form_id), {})
                selected_ids: list[str] = []
                seen: set[str] = set()
                for idx in indices:
                    try:
                        i = int(idx)
                    except Exception:
                        continue
                    option_id = mapping.get(i)
                    if not option_id or option_id in seen:
                        continue
                    seen.add(option_id)
                    selected_ids.append(option_id)

                conn.execute(
                    text(
                        """
                        UPDATE eventpaymententry
                        SET selected_option_indices = :raw_ids
                        WHERE id = :entry_id;
                        """
                    ),
                    {
                        "raw_ids": json.dumps(selected_ids) if selected_ids else None,
                        "entry_id": entry_id,
                    },
                )

        if has_entry_indices and not has_entry_ids:
            logger.info("Renaming selected_option_indices to selected_option_ids...")
            conn.execute(
                text(
                    """
                    ALTER TABLE eventpaymententry
                    RENAME COLUMN selected_option_indices TO selected_option_ids;
                    """
                )
            )

        if has_form_options:
            logger.info("Dropping legacy eventpaymentform.options column...")
            conn.execute(
                text(
                    """
                    ALTER TABLE eventpaymentform
                    DROP COLUMN options;
                    """
                )
            )

        logger.info("Migration 027 completed successfully.")
