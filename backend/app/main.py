from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
import os
import time
import logging
from sqlalchemy.exc import OperationalError
from contextlib import asynccontextmanager
from app.database import create_db_and_tables
from app.api import auth, organizations, events, ics, users, upload, subscriptions, oidc, groups, tags, organization_links

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
            break
        except OperationalError as e:
            retries -= 1
            logger.warning(f"Database connection failed. Retrying in 2 seconds... ({retries} retries left)")
            logger.warning(f"Error: {e}")
            time.sleep(2)
    
    if retries == 0:
        logger.error("Could not connect to the database after multiple attempts.")
        raise Exception("Database connection failed")
        
    yield

app = FastAPI(title="Calend'INT API", lifespan=lifespan)

# Add SessionMiddleware for OIDC
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "your-secret-key-change-in-production-please-make-it-long-and-random")
)


app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(oidc.router, prefix="/auth", tags=["oidc"])
app.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
app.include_router(events.router, prefix="/events", tags=["events"])
app.include_router(ics.router, prefix="/calendar", tags=["calendar"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(upload.router, prefix="/upload", tags=["upload"])
app.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])
app.include_router(groups.router, tags=["groups"])
app.include_router(tags.router, tags=["tags"])
app.include_router(organization_links.router, tags=["organization-links"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Calend'INT API"}
