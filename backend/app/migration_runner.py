from datetime import datetime
import glob
import importlib.util
import logging
import os
from pathlib import Path
import re
import subprocess

from lockfile import AlreadyLocked, LockFile

logger = logging.getLogger(__name__)

MIGRATION_DIR = Path(__file__).parent.parent / "migrations"
STATE_DIR = Path("/app/migration_state")
STATE_FILE = STATE_DIR / "last_migration"

def ensure_state_dir():
    if not STATE_DIR.exists():
        STATE_DIR.mkdir(parents=True, exist_ok=True)

def get_last_migration():
    if not STATE_FILE.exists():
        return None
    try:
        return int(STATE_FILE.read_text().strip())
    except ValueError:
        return 0

def set_last_migration(number):
    ensure_state_dir()
    STATE_FILE.write_text(str(number))

def get_available_migrations():
    files = glob.glob(str(MIGRATION_DIR / "*.py"))
    migrations = []
    for f in files:
        filename = os.path.basename(f)
        match = re.match(r"^(\d+)_.*\.py$", filename)
        if match:
            migrations.append((int(match.group(1)), f))
    return sorted(migrations, key=lambda x: x[0])

def dump_database(number):
    """Dump the database to a SQL file in the migration directory."""
    db_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/calendint")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dump_file = STATE_DIR / f"dump_{number:03}_{timestamp}.sql"
    
    logger.info(f"Dumping database to {dump_file}...")
    try:
        # PGPASSWORD might be needed if not in URL, but usually pg_dump handles full connection strings
        # We rely on the environment having access or .pgpass
        subprocess.run(["pg_dump", db_url, "-f", str(dump_file)], check=True)
        logger.info("Database dump successful.")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        logger.warning(f"Failed to dump database: {e}")

def run_migrations():
    ensure_state_dir()
    
    available = get_available_migrations()
    if not available:
        logger.info("No migrations found.")
        return

    max_migration = available[-1][0]
    lock = LockFile(STATE_FILE)
    try:
        lock.acquire(-1)
    except AlreadyLocked:
        logger.info("Migration is already running, skipping.")
        return
    try:
        last_run = get_last_migration()

        if last_run is None:
            # First boot (or state lost).
            # User requested: "on first boot, save the current last migration step as the last one completed when creating the database"
            # We assume that creating the DB (which happens before this in main.py) brings us up to date with CURRENT models.
            # Thus we skip all existing migrations and mark the state as up to date.
            logger.info(f"First run detected. Setting migration state to {max_migration} without running scripts.")
            set_last_migration(max_migration)
            return

        logger.info(f"Last applied migration: {last_run}")

        pending_migrations = [m for m in available if m[0] > last_run]
        
        if pending_migrations:
            dump_database(last_run)
            
        for number, filepath in pending_migrations:
            logger.info(f"Applying migration {number}: {os.path.basename(filepath)}")
            try:
                # Load module dynamically
                spec = importlib.util.spec_from_file_location(f"migration_{number}", filepath)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    if hasattr(module, "run_migration"):
                        module.run_migration()
                    else:
                        logger.warning(f"Migration {number} has no run_migration() function.")
                    
                    # Update state after success
                    set_last_migration(number)
                    last_run = number
            except Exception as e:
                logger.error(f"Failed to run migration {number}: {e}")
                # Stop migration process on error
                raise e
    finally:
        lock.release()
    logger.info("Migrations completed.")
