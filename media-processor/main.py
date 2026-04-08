"""
media-processor — watches storedfile rows and generates WebP/WebM variants.
"""

import io
import json
import logging
import os
import subprocess
import time
from pathlib import Path
from uuid import UUID

import psycopg2
import psycopg2.extras
from minio import Minio
from PIL import Image

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DATABASE_URL: str = os.environ["DATABASE_URL"]
MINIO_ENDPOINT: str = os.environ["MINIO_ENDPOINT"]
MINIO_ACCESS_KEY: str = os.environ["MINIO_ACCESS_KEY"]
MINIO_SECRET_KEY: str = os.environ["MINIO_SECRET_KEY"]
MINIO_BUCKET: str = os.environ.get("MINIO_BUCKET", "calendint")
MINIO_SECURE: bool = os.environ.get("MINIO_SECURE", "false").lower() == "true"
MEDIA_SIZES: list[int] = sorted(
    int(s)
    for s in os.environ.get("MEDIA_SIZES", "320,640,960,1280,1920").split(",")
    if s.strip()
)
POLL_INTERVAL: int = int(os.environ.get("POLL_INTERVAL", "10"))
MAX_RETRIES: int = 3
RESET_RETRIES_ON_START: bool = os.environ.get("RESET_RETRIES_ON_START", "false").lower() == "true"


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------


def connect_db() -> psycopg2.extensions.connection:
    """Connect to PostgreSQL, retrying until ready."""
    while True:
        try:
            conn = psycopg2.connect(
                DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor
            )
            conn.autocommit = False
            log.info("Connected to database.")
            return conn
        except Exception as exc:
            log.warning("DB not ready (%s), retrying in 5s…", exc)
            time.sleep(5)


def connect_minio() -> Minio:
    """Connect to MinIO, retrying until ready."""
    client = Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=MINIO_SECURE,
    )
    while True:
        try:
            client.bucket_exists(MINIO_BUCKET)
            log.info("Connected to MinIO.")
            return client
        except Exception as exc:
            log.warning("MinIO not ready (%s), retrying in 5s…", exc)
            time.sleep(5)


# ---------------------------------------------------------------------------
# Image processing
# ---------------------------------------------------------------------------


def _upload_bytes(
    minio_client: Minio, bucket: str, object_name: str, data: bytes, content_type: str
) -> None:
    minio_client.put_object(
        bucket,
        object_name,
        io.BytesIO(data),
        length=len(data),
        content_type=content_type,
    )


def _generate_webp_variants(
    img: Image.Image,
    stem: str,
    sizes: list[int],
    minio_client: Minio,
    bucket: str,
) -> list[dict]:
    """Resize `img` to each width in `sizes` (skip if wider than original) and
    upload as WebP. Returns list of variant dicts."""
    variants: list[dict] = []
    orig_w, orig_h = img.size

    for width in sizes:
        if width > orig_w:
            continue
        height = round(orig_h * width / orig_w)
        resized = img.resize((width, height), Image.LANCZOS)
        buf = io.BytesIO()
        resized.save(buf, format="WEBP", quality=85)
        data = buf.getvalue()

        object_name = f"{width}_{stem}.webp"
        _upload_bytes(minio_client, bucket, object_name, data, "image/webp")
        log.info("  Uploaded variant %s (%d bytes)", object_name, len(data))
        variants.append(
            {
                "width": width,
                "url": f"/uploads/{object_name}",
                "format": "webp",
                "size": len(data),
            }
        )

    return variants


# ---------------------------------------------------------------------------
# Video processing
# ---------------------------------------------------------------------------


def _run_ffmpeg_with_tempfile(args: list[str], input_data: bytes) -> bytes:
    """Write input to a temp file and run ffmpeg — needed for seekable formats (MP4, MOV…)."""
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".input", delete=False) as tmp:
        tmp.write(input_data)
        tmp_path = tmp.name
    try:
        # Replace placeholder "INPUT" in args with the actual temp path
        resolved = [tmp_path if a == "INPUT" else a for a in args]
        proc = subprocess.run(
            ["ffmpeg", "-y"] + resolved,
            capture_output=True,
            timeout=300,
        )
        if proc.returncode != 0:
            raise RuntimeError(
                f"ffmpeg failed: {proc.stderr.decode(errors='replace')[:800]}"
            )
        return proc.stdout
    finally:
        import os as _os

        _os.unlink(tmp_path)


def _generate_video_variants(
    data: bytes,
    stem: str,
    sizes: list[int],
    minio_client: Minio,
    bucket: str,
) -> list[dict]:
    """Generate WebP thumbnails + one WebM transcode for a video."""
    variants: list[dict] = []

    # --- Extract thumbnail at 1 second ---
    try:
        thumb_png = _run_ffmpeg_with_tempfile(
            [
                "-i",
                "INPUT",
                "-ss",
                "00:00:01",
                "-vframes",
                "1",
                "-f",
                "image2pipe",
                "-vcodec",
                "png",
                "pipe:1",
            ],
            data,
        )
        img = Image.open(io.BytesIO(thumb_png))
        webp_variants = _generate_webp_variants(img, stem, sizes, minio_client, bucket)
        variants.extend(webp_variants)
    except Exception as exc:
        log.warning("  Could not extract thumbnail: %s", exc)

    # --- Transcode to WebM (VP9 + Opus, max 1280px wide) ---
    try:
        webm_data = _run_ffmpeg_with_tempfile(
            [
                "-i",
                "INPUT",
                "-c:v",
                "libvpx-vp9",
                "-crf",
                "33",
                "-b:v",
                "0",
                "-vf",
                "scale='min(1280,iw)':-2",
                "-c:a",
                "libopus",
                "-b:a",
                "128k",
                "-f",
                "webm",
                "pipe:1",
            ],
            data,
        )
        object_name = f"720p_{stem}.webm"
        _upload_bytes(minio_client, bucket, object_name, webm_data, "video/webm")
        log.info("  Uploaded WebM variant %s (%d bytes)", object_name, len(webm_data))
        variants.append(
            {
                "width": 1280,
                "url": f"/uploads/{object_name}",
                "format": "webm",
                "size": len(webm_data),
            }
        )
    except Exception as exc:
        log.warning("  Could not transcode to WebM: %s", exc)

    return variants


# ---------------------------------------------------------------------------
# Per-file processing
# ---------------------------------------------------------------------------


def process_file(
    conn: psycopg2.extensions.connection,
    minio_client: Minio,
    bucket: str,
    row: dict,
    sizes: list[int],
) -> None:
    file_id: str = str(row["id"])
    stored_filename: str = row["stored_filename"]
    content_type: str = row["content_type"]
    file_type: str = row["file_type"]

    log.info("Processing file %s (%s, %s)", stored_filename, file_type, content_type)

    # Download from MinIO
    response = minio_client.get_object(bucket, stored_filename)
    try:
        data: bytes = response.read()
    finally:
        response.close()
        response.release_conn()

    # Derive a safe stem (no extension)
    stem = Path(stored_filename).stem

    variants: list[dict] = []

    if content_type == "image/svg+xml":
        # SVGs scale natively — mark processed with empty variants
        log.info("  SVG detected, skipping transcoding.")
    elif file_type == "image":
        img = Image.open(io.BytesIO(data))
        img = img.convert("RGBA") if img.mode in ("P", "RGBA") else img.convert("RGB")
        variants = _generate_webp_variants(img, stem, sizes, minio_client, bucket)
    elif file_type == "video":
        variants = _generate_video_variants(data, stem, sizes, minio_client, bucket)
    else:
        log.warning(
            "  Unknown file_type '%s', marking processed with no variants.", file_type
        )

    # Persist
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE storedfile SET processed = TRUE, variants = %s WHERE id = %s",
            (json.dumps(variants), file_id),
        )
    conn.commit()
    log.info("  Done — %d variant(s) stored.", len(variants))


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------


def reset_retries(conn: psycopg2.extensions.connection) -> None:
    """Reset retry_count to 0 for all unprocessed files."""
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE storedfile SET retry_count = 0 WHERE processed = FALSE AND retry_count > 0"
        )
        count = cur.rowcount
    conn.commit()
    log.info("Reset retry_count for %d unprocessed file(s).", count)


def main() -> None:
    log.info(
        "Starting media-processor (sizes=%s, interval=%ds, reset_retries=%s)",
        MEDIA_SIZES,
        POLL_INTERVAL,
        RESET_RETRIES_ON_START,
    )
    conn = connect_db()
    minio_client = connect_minio()

    if RESET_RETRIES_ON_START:
        reset_retries(conn)

    while True:
        try:
            # Reconnect if the connection was lost
            if conn.closed:
                conn = connect_db()

            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, stored_filename, url, content_type, file_type
                    FROM storedfile
                    WHERE processed = FALSE AND retry_count < %s
                    LIMIT 5
                    """,
                    (MAX_RETRIES,),
                )
                rows = cur.fetchall()

            if not rows:
                time.sleep(POLL_INTERVAL)
                continue

            for row in rows:
                file_id = str(row["id"])
                try:
                    process_file(conn, minio_client, MINIO_BUCKET, row, MEDIA_SIZES)
                except Exception as exc:
                    log.error("Failed to process %s: %s", row["stored_filename"], exc)
                    try:
                        with conn.cursor() as cur:
                            cur.execute(
                                "UPDATE storedfile SET retry_count = retry_count + 1 WHERE id = %s",
                                (file_id,),
                            )
                        conn.commit()
                    except Exception as db_exc:
                        log.error("Could not increment retry_count: %s", db_exc)
                        conn.rollback()

        except Exception as exc:
            log.error("Unexpected error in main loop: %s", exc)
            try:
                conn.rollback()
            except Exception:
                pass
            time.sleep(POLL_INTERVAL)

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
