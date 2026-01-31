import asyncio
from contextlib import asynccontextmanager
import logging
import os
import time

from dotenv import load_dotenv
from fastapi import FastAPI
from sqlalchemy.exc import OperationalError
from sqlmodel import Session
from starlette.middleware.sessions import SessionMiddleware

from app.api import (
    admin,
    auth,
    cas,
    events,
    groups,
    ics,
    notifications,
    organization_links,
    organizations,
    short_links,
    subscriptions,
    tags,
    upload,
    users,
)
from app.api.notifications import process_notifications
from app.database import create_db_and_tables
from app.database import engine
from app.migration_runner import run_migrations


# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    retries = 30
    while retries > 0:
        try:
            create_db_and_tables()
            logger.info("Database connection successful and tables created.")
            run_migrations()
            break
        except OperationalError as e:
            retries -= 1
            logger.warning(f"Database connection failed. Retrying in 2 seconds... ({retries} retries left)")
            logger.warning(f"Error: {e}")
            time.sleep(2)
    
    if retries == 0:
        logger.error("Could not connect to the database after multiple attempts.")
        raise Exception("Database connection failed")

    # Start notification loop
    async def notification_loop():
        def run_check():
            with Session(engine) as session:
                return process_notifications(session)

        while True:
            try:
                cron_delay = int(os.getenv("CRON_DELAY", "900"))
                logger.info("Running notification check...")
                
                count = await asyncio.to_thread(run_check)
                
                if count > 0:
                    logger.info(f"Sent {count} notifications")
                await asyncio.sleep(cron_delay)
            except Exception as e:
                logger.error(f"Error in notification loop: {e}")
                await asyncio.sleep(60) # Wait a bit before retrying

    task = asyncio.create_task(notification_loop())
        
    yield

    task.cancel()

app = FastAPI(title="Calend'INT API", lifespan=lifespan)

# Add SessionMiddleware for OIDC
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "your-secret-key-change-in-production-please-make-it-long-and-random")
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(cas.router, prefix="/auth", tags=["cas"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
app.include_router(events.router, prefix="/events", tags=["events"])
app.include_router(ics.router, prefix="/calendar", tags=["calendar"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(upload.router, prefix="/upload", tags=["upload"])
app.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])
app.include_router(groups.router, tags=["groups"])
app.include_router(tags.router, tags=["tags"])
app.include_router(organization_links.router, tags=["organization-links"])
app.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
app.include_router(short_links.router, prefix="/short-links", tags=["short-links"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Calend'INT API"}
