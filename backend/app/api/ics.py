from datetime import datetime, timezone
import hashlib
from urllib.parse import urlparse
from uuid import UUID
from dateutil import tz

from fastapi import APIRouter, Depends, HTTPException, Response
from icalendar import Calendar, Event as IcalEvent, vCalAddress, vText
from sqlmodel import Session, and_, col, func, or_, select
from starlette.config import Config

from app.api.auth import get_current_user
from app.api.events import get_history_cutoff_condition, get_visibility_conditions
from app.database import get_session
from app.models import (
    Event,
    EventReaction,
    EventTag,
    EventVisibility,
    GroupMembership,
    Membership,
    Subscription,
    User,
)

# Increase this counter by one each time you make changes to the calendar generation logic
# This ensure that the calendars will update properly
ICS_GENERATOR_VERSION = 1

config = Config(".env")
BASE_URL = config.get("APP_BASE_URL")
MAIL_DOMAIN = urlparse(BASE_URL).hostname or BASE_URL
APP_TIMEZONE = tz.gettz(config.get("APP_TIMEZONE", default="UTC"))

assert BASE_URL is not None, "APP_BASE_URL must be set in .env"
assert config.get("SECRET_KEY") is not None, "SECRET_KEY must be set in .env"
assert APP_TIMEZONE is not None, "APP_TIMEZONE must be a valid timezone"


def securekey_gen(user_id: str | UUID):
    global_key = config.get("SECRET_KEY")
    return hashlib.sha256(f"{global_key}{user_id}".encode()).hexdigest()[:16]


router = APIRouter()


@router.get("/{securekey}/{user_id}.ics")
def export_user_calendar(
    securekey: str, user_id: str, session: Session = Depends(get_session)
):
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
        conditions.append(col(Event.organization_id).in_(all_org_ids))

    # 2. Subscribed Tags
    if sub_tag_ids:
        # Efficiently filter events that have any of the subscribed tags
        # Fetch EventTag objects to safely get event_ids
        event_tags = session.exec(
            select(EventTag).where(col(EventTag.tag_id).in_(sub_tag_ids))
        ).all()
        tag_event_ids = [et.event_id for et in event_tags]

        if tag_event_ids:
            conditions.append(col(Event.id).in_(tag_event_ids))

    # 3. Private Events (Group Membership)
    if user_group_ids:
        conditions.append(col(Event.group_id).in_(user_group_ids))

    # 4. Reacted Events
    if reacted_event_ids:
        conditions.append(col(Event.id).in_(reacted_event_ids))

    # 5. Featured Events
    conditions.append(Event.featured > 0)

    if not conditions:
        events = []
    else:
        # Apply strict visibility rules from events system to ensure consistency
        visibility_conditions = get_visibility_conditions(user, session)

        # Hide events that are too old, sharing the cutoff logic with the
        # calendar view (see app/api/events.py).
        time_condition = get_history_cutoff_condition(user, session)

        clauses = [or_(*conditions), visibility_conditions]
        if time_condition is not None:
            clauses.append(time_condition)

        query = select(Event).where(and_(*clauses))
        events = session.exec(query).unique().all()

    # Create iCalendar
    cal = Calendar()
    cal.add("prodid", "-//Calend'INT//mxm.dk//")
    cal.add("version", "2.0")
    cal.add("X-WR-CALNAME", "Calend'INT")
    cal.add("X-WR-TIMEZONE", config.get("APP_TIMEZONE", default="UTC"))

    now_utc = datetime.now(timezone.utc)

    for event in events:
        ievent = IcalEvent()
        organization_name = event.organization.name if event.organization else ""
        ievent.add("summary", f"{organization_name} : {event.title}")
        ievent.add("dtstart", event.start_time.astimezone(tz=APP_TIMEZONE))
        ievent.add("dtend", event.end_time.astimezone(tz=APP_TIMEZONE))
        # DTSTAMP = time this particular revision of the event was generated (RFC 5545 §3.8.7.2)
        ievent.add("dtstamp", now_utc)
        ievent.add("uid", f"{event.id}@{BASE_URL}")
        # SEQUENCE tells Google Calendar (and others) that this is a newer revision
        ievent.add("sequence", (event.sequence or 0) + ICS_GENERATOR_VERSION)
        # LAST-MODIFIED = when the event content last changed
        last_modified = event.updated_at or event.created_at
        ievent.add("last-modified", last_modified.astimezone(timezone.utc))

        # Build description with poster and event link
        description_parts = []
        if event.description:
            description_parts.append(event.description)
        if organization_name:
            description_parts.append(f"\n\nOrganisé par: {organization_name}")

        # Add event link
        event_url = f"{BASE_URL}/events/{event.id}"
        ievent.add("url", event_url)
        description_parts.append(f"\n\nVoir l'événement: {event_url}")

        if description_parts:
            ievent.add("description", "\n".join(description_parts))

        if event.location:
            ievent.add("location", event.location)

        # ORGANIZER — main hosting organization
        if event.organization:
            organizer = vCalAddress(f"mailto:{event.organization.slug}@{MAIL_DOMAIN}")
            organizer.params["cn"] = vText(organization_name)
            ievent.add("organizer", organizer)

        # ATTENDEEs — guest organizations as co-organizers (ROLE=CHAIR per RFC 5545)
        for guest in event.guest_organizations:
            attendee = vCalAddress(f"mailto:{guest.slug}@{MAIL_DOMAIN}")
            attendee.params["cn"] = vText(guest.name)
            attendee.params["cutype"] = vText("GROUP")
            attendee.params["role"] = vText("CHAIR")
            attendee.params["partstat"] = vText("ACCEPTED")
            ievent.add("attendee", attendee, encode=False)

        cal.add_component(ievent)

    return Response(
        content=cal.to_ical(),
        media_type="text/calendar",
        headers={
            "Content-Disposition": f"attachment; filename=calendint-{user.email.split('@')[0]}.ics"
        },
    )


@router.get("/securekey")
def get_securekey(current_user: User = Depends(get_current_user)):
    return securekey_gen(current_user.id)
