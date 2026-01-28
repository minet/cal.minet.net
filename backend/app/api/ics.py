from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import Session, select, or_, and_, func
from app.database import get_session
from starlette.config import Config
from app.models import (
    Event, 
    User, 
    Subscription, 
    Membership, 
    GroupMembership,
    EventTag,
    EventVisibility,
    EventReaction
)
from app.api.auth import get_current_user
from icalendar import Calendar, Event as IcalEvent
from datetime import datetime, timezone
from uuid import UUID
import hashlib

config = Config('.env')
BASE_URL = config.get("APP_BASE_URL")

assert BASE_URL is not None, "APP_BASE_URL must be set in .env"
assert config.get("SECRET_KEY") is not None, "SECRET_KEY must be set in .env"


def securekey_gen(user_id: str | UUID):
    global_key = config.get("SECRET_KEY")
    return hashlib.sha256(f"{global_key}{user_id}".encode()).hexdigest()[:16]

router = APIRouter()

@router.get("/{securekey}/{user_id}.ics")
def export_user_calendar(securekey: str, user_id: str, session: Session = Depends(get_session)):
    """
    Export personal calendar including:
    - Events from organizations the user is a member of
    - Events from subscribed organizations
    """
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    # Check if the user exists
    user = session.get(User, user_uuid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify user exists
    if securekey != securekey_gen(user_id):
        raise HTTPException(status_code=401, detail="Invalid secure key")

    # Get user memberships
    # Get user membership organization IDs
    memberships = session.exec(
        select(Membership).where(Membership.user_id == user_uuid)
    ).all()
    member_org_ids = [m.organization_id for m in memberships]
    
    # Get user subscriptions (Orgs and Tags)
    subscriptions = session.exec(
        select(Subscription).where(Subscription.user_id == user_uuid)
    ).all()
    sub_org_ids = [s.organization_id for s in subscriptions if s.organization_id]
    sub_tag_ids = [s.tag_id for s in subscriptions if s.tag_id]
    
    # Get user group memberships
    group_memberships = session.exec(
        select(GroupMembership).where(GroupMembership.user_id == user_uuid)
    ).all()
    user_group_ids = [gm.group_id for gm in group_memberships]
    
    # Get user reacted events
    # We fetch event IDs where the user has any reaction
    reacted_events = session.exec(
        select(EventReaction).where(EventReaction.user_id == user_uuid)
    ).all()
    reacted_event_ids = list(set([r.event_id for r in reacted_events]))
    # Combine Organization IDs (Membership + Subscription)
    all_org_ids = list(set(member_org_ids + sub_org_ids))
    
    # Build Query Conditions
    conditions = []
    
    # 1. Subscribed Organizations
    if all_org_ids:
        conditions.append(Event.organization_id.in_(all_org_ids))
        
    # 2. Subscribed Tags
    if sub_tag_ids:
        # Efficiently filter events that have any of the subscribed tags
        # Fetch EventTag objects to safely get event_ids
        event_tags = session.exec(
            select(EventTag).where(EventTag.tag_id.in_(sub_tag_ids))
        ).all()
        tag_event_ids = [et.event_id for et in event_tags]
        
        if tag_event_ids:
            conditions.append(Event.id.in_(tag_event_ids))
            
    # 3. Private Events (Group Membership)
    if user_group_ids:
        conditions.append(Event.group_id.in_(user_group_ids))
            
    # 4. Reacted Events
    if reacted_event_ids:
        conditions.append(Event.id.in_(reacted_event_ids))
            
    if reacted_event_ids:
        conditions.append(Event.id.in_(reacted_event_ids))
    
    # 5. Featured Events
    conditions.append(Event.featured > 0)

    if not conditions:
        events = []
    else:
        # Base filter: No Drafts and not rejected
        query = select(Event).where(
            Event.visibility != EventVisibility.DRAFT,
            Event.visibility != EventVisibility.PUBLIC_REJECTED,
            or_(*conditions)
        )
        events = session.exec(query).unique().all()
    
    # Create iCalendar
    cal = Calendar()
    cal.add('prodid', '-//Calend\'INT Personal Calendar//mxm.dk//')
    cal.add('version', '2.0')
    cal.add('X-WR-CALNAME', 'Mon calendrier Calend\'INT')
    cal.add('X-WR-TIMEZONE', 'Europe/Paris')
    
    for event in events:
        ievent = IcalEvent()
        ievent.add('summary', event.title)
        ievent.add('dtstart', event.start_time)
        ievent.add('dtend', event.end_time)
        ievent.add('dtstamp', datetime.now(timezone.utc))
        ievent.add('uid', f'{event.id}@{BASE_URL}')
        
        # Build description with poster and event link
        description_parts = []
        if event.description:
            description_parts.append(event.description)
        
        
        # Add event link
        event_url = f"{BASE_URL}/events/{event.id}"
        ievent.add('url', event_url)
        description_parts.append(f"\n\nVoir l'événement: {event_url}")
        
        if description_parts:
            ievent.add('description', '\n'.join(description_parts))
            
        if event.location:
            ievent.add('location', event.location)
            
        cal.add_component(ievent)
    
    return Response(
        content=cal.to_ical(),
        media_type="text/calendar",
        headers={"Content-Disposition": f"attachment; filename=calendint-{user.email.split('@')[0]}.ics"}
    )


@router.get("/securekey")
def get_securekey(current_user: User = Depends(get_current_user)):
    return securekey_gen(current_user.id)
