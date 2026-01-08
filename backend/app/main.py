from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
import os
from app.database import create_db_and_tables
from app.api import auth, organizations, events, ics, users, upload, subscriptions, oidc, groups, tags, organization_links

# Load environment variables
load_dotenv()

app = FastAPI(title="Calend'INT API")

# Add SessionMiddleware for OIDC
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "your-secret-key-change-in-production-please-make-it-long-and-random")
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

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
