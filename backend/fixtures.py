import os
import sys
from datetime import datetime, timedelta

# Ensure app can be imported
sys.path.append(os.getcwd())

from sqlmodel import Session, select, create_engine
from app.models import Organization, OrganizationLink, Event, EventGuestOrganization, OrganizationType, User, EventVisibility
from uuid import uuid4

# Use default from docker-compose if env not set, but localhost for host-running
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/calendint")

print(f"Connecting to {DATABASE_URL}")
engine = create_engine(DATABASE_URL)

def create_fixtures():
    with Session(engine) as session:
        # 1. Create Organizations if not exist
        # Demo Org 1
        org1 = session.exec(select(Organization).where(Organization.slug == "demo-club")).first()
        if not org1:
            org1 = Organization(
                name="Demo Club",
                slug="demo-club",
                type=OrganizationType.CLUB,
                description="A club for demonstrating new features like custom links.",
                color_chroma=0.15,
                color_hue=250.0 # Blue/Purple
            )
            session.add(org1)
            session.commit()
            print("Created Demo Club")
        else:
            print("Demo Club already exists")
        
        # Companion Org
        org2 = session.exec(select(Organization).where(Organization.slug == "partner-assoc")).first()
        if not org2:
            org2 = Organization(
                name="Partner Association",
                slug="partner-assoc",
                type=OrganizationType.ASSOCIATION,
                color_chroma=0.18,
                color_hue=30.0 # Orange/Red
            )
            session.add(org2)
            session.commit()
            print("Created Partner Association")
        else:
            print("Partner Association already exists")

        session.refresh(org1)
        session.refresh(org2)

        # 2. Add Links to Org 1
        link1 = session.exec(select(OrganizationLink).where(OrganizationLink.organization_id == org1.id, OrganizationLink.name == "Website")).first()
        if not link1:
            link1 = OrganizationLink(organization_id=org1.id, name="Website", url="https://example.com", order=1)
            session.add(link1)
            print("Added Website link")
        
        link2 = session.exec(select(OrganizationLink).where(OrganizationLink.organization_id == org1.id, OrganizationLink.name == "Discord")).first()
        if not link2:
            link2 = OrganizationLink(organization_id=org1.id, name="Discord", url="https://discord.gg/example", order=2)
            session.add(link2)
            print("Added Discord link")
        
        session.commit()

        # 3. Create Event with Guest Org
        # Check if event exists
        event = session.exec(select(Event).where(Event.title == "Joint Gala")).first()
        if not event:
            # Need a creator.
            user = session.exec(select(User)).first()
            if user:
                start_time = datetime.utcnow() + timedelta(days=5)
                end_time = start_time + timedelta(hours=6)
                
                event = Event(
                    title="Joint Gala",
                    description="A gala hosted by Demo Club and Partner Association. Come join us!",
                    start_time=start_time,
                    end_time=end_time,
                    location="Grand Hall",
                    organization_id=org1.id,
                    created_by_id=user.id,
                    visibility=EventVisibility.PUBLIC_APPROVED,
                    show_on_schedule=True
                )
                session.add(event)
                session.commit()
                session.refresh(event)
                
                # Add guest
                guest_link = EventGuestOrganization(event_id=event.id, organization_id=org2.id)
                session.add(guest_link)
                session.commit()
                print("Created Joint Gala with Guest Org")
            else:
                print("No user found, skipping event creation")
        else:
            print("Joint Gala event already exists")

if __name__ == "__main__":
    create_fixtures()
