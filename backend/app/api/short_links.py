from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
from uuid import UUID
import random
import string
import os

from app.database import get_session
from app.models import ShortLink, ShortLinkType, ShortLinkActionType, User, Event, Organization, Membership, Role, EventVisibility
from app.api.auth import get_current_user, get_current_user_optional
from app.schemas import ShortLinkCreate, ShortLinkRead, ShortLinkInfo, Message
from app.api.events import can_view_event, get_org_membership

router = APIRouter()

def generate_short_id(length=3):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@router.post("/", response_model=ShortLinkRead)
def create_short_link(
    link_data: ShortLinkCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Create a new short link"""
    # 1. Validate Item and Permissions
    item_id = UUID(link_data.item_id)
    
    if link_data.item_type == ShortLinkType.ORGANIZATION:
        org = session.get(Organization, item_id)
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")
        # Only members can share organization links
        membership = get_org_membership(current_user, item_id, session)
        if not (membership or current_user.is_superadmin):
             raise HTTPException(status_code=403, detail="Must be a member to share organization")
             
    elif link_data.item_type == ShortLinkType.EVENT:
        event = session.get(Event, item_id)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        # Check if user can see the event
        if not (can_view_event(event, current_user, session) or current_user.is_superadmin):
             raise HTTPException(status_code=403, detail="Not authorized to share this event")
             
    elif link_data.item_type == ShortLinkType.TAG:
        if link_data.action_type != ShortLinkActionType.SUBSCRIBE:
             raise HTTPException(status_code=400, detail="Tags can only be shared for subscription")
             
        # Assuming similar logic for tags, usually tied to Org
        # For now, let's say only Org members can share tags too if they belong to an org
        from app.models import Tag
        tag = session.get(Tag, item_id)
        if not tag:
             raise HTTPException(status_code=404, detail="Tag not found")
        membership = get_org_membership(current_user, tag.organization_id, session)
        if not (membership or current_user.is_superadmin):
             raise HTTPException(status_code=403, detail="Must be a member to share tag")
             
    else:
        raise HTTPException(status_code=400, detail="Invalid item type")

    # 2. Check if identical link already exists
    existing = session.exec(
        select(ShortLink).where(
            ShortLink.item_type == link_data.item_type,
            ShortLink.item_id == item_id,
            ShortLink.action_type == link_data.action_type
        )
    ).first()
    
    app_base_url = os.getenv("APP_BASE_URL", "https://cal.minet.net")
    
    if existing:
        return ShortLinkRead(id=existing.id, url=f"{app_base_url}/s/{existing.id}")

    # 3. Create new link
    # Try to generate unique ID
    for _ in range(10): # Retry a few times
        new_id = generate_short_id(3) # Start with 3
        if not session.get(ShortLink, new_id):
            break
    else:
        # If 3 chars fail, try 4
        new_id = generate_short_id(4)
        if session.get(ShortLink, new_id):
             raise HTTPException(status_code=500, detail="Failed to generate unique ID")

    new_link = ShortLink(
        id=new_id,
        item_type=ShortLinkType(link_data.item_type),
        action_type=ShortLinkActionType(link_data.action_type),
        item_id=item_id,
        created_by_id=current_user.id
    )
    
    session.add(new_link)
    session.commit()
    session.refresh(new_link)
    
    return ShortLinkRead(id=new_link.id, url=f"{app_base_url}/s/{new_link.id}")

@router.get("/visit/{short_id}")
def visit_short_link(
    short_id: str,
    session: Session = Depends(get_session)
):
    """Resolve short link and return redirect URL or action"""
    link = session.get(ShortLink, short_id)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    # Update last used
    link.last_used_at = datetime.utcnow()
    session.add(link)
    session.commit()
    
    app_base_url = os.getenv("APP_BASE_URL", "https://cal.minet.net")
    
    # Direct Redirect
    if link.action_type in [ShortLinkActionType.VIEW, ShortLinkActionType.COUNTDOWN]:
        if link.item_type == ShortLinkType.EVENT:
            if link.action_type == ShortLinkActionType.COUNTDOWN:
                return RedirectResponse(url=f"{app_base_url}/events/{link.item_id}/countdown")
            return RedirectResponse(url=f"{app_base_url}/events/{link.item_id}")
            
        elif link.item_type == ShortLinkType.ORGANIZATION:
             return RedirectResponse(url=f"{app_base_url}/organizations/{link.item_id}")
             
    # Subscribe flow -> Redirect to Consent Page
    if link.action_type == ShortLinkActionType.SUBSCRIBE:
        return RedirectResponse(url=f"{app_base_url}/consent/{link.id}") # Route to frontend consent page
    
    return RedirectResponse(url=f"{app_base_url}") # Fallback

@router.get("/info/{short_id}", response_model=ShortLinkInfo)
def get_link_info(
    short_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get info for confirmation page (Logged in users only)"""
    link = session.get(ShortLink, short_id)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
        
    title = "Unknown"
    logo_url = None
    description = None
    color_chroma = None
    color_hue = None
    tag_color = None

    if link.item_type == ShortLinkType.EVENT:
        event = session.get(Event, link.item_id)
        if event:
            # Check visibility
             if not can_view_event(event, current_user, session):
                 raise HTTPException(status_code=403, detail="Not authorized to see this event")
             title = event.title
             # Maybe show date in description?
             description = f"Date: {event.start_time.strftime('%d/%m/%Y %H:%M')}"
             if event.organization:
                 logo_url = event.organization.logo_url
                 color_chroma = event.organization.color_chroma
                 color_hue = event.organization.color_hue
             
    elif link.item_type == ShortLinkType.ORGANIZATION:
        org = session.get(Organization, link.item_id)
        if org:
            title = org.name
            description = org.description
            logo_url = org.logo_url
            color_chroma = org.color_chroma
            color_hue = org.color_hue
            
    if link.item_type == ShortLinkType.TAG:
        from app.models import Tag
        tag = session.get(Tag, link.item_id)
        if tag:
            title = tag.name
            tag_color = tag.color
            # Tags might be part of an org
            org = session.get(Organization, tag.organization_id)
            if org:
                logo_url = org.logo_url
                color_chroma = org.color_chroma
                color_hue = org.color_hue
            
    return ShortLinkInfo(
        id=link.id,
        title=title,
        description=description,
        item_type=link.item_type,
        item_id=link.item_id,
        logo_url=logo_url,
        color_chroma=color_chroma,
        color_hue=color_hue,
        tag_color=tag_color
    )

@router.post("/confirm/{short_id}", response_model=Message)
def confirm_subscription(
    short_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Execute the subscription action"""
    link = session.get(ShortLink, short_id)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    if link.action_type != ShortLinkActionType.SUBSCRIBE:
        raise HTTPException(status_code=400, detail="Not a subscription link")
        
    if link.item_type == ShortLinkType.ORGANIZATION:
        # Subscribe to Organization
        from app.models import Subscription
        # Check if already subscribed
        existing = session.exec(
            select(Subscription).where(
                Subscription.user_id == current_user.id, 
                Subscription.organization_id == link.item_id
            )
        ).first()
        
        if not existing:
            sub = Subscription(
                user_id=current_user.id,
                organization_id=link.item_id,
                subscribe_all=False # Default? Or maybe ask user? Prompt implied "subscribe to tag/org or add event"
            )
            session.add(sub)
            
    elif link.item_type == ShortLinkType.TAG:
         from app.models import Subscription
         existing = session.exec(
            select(Subscription).where(
                Subscription.user_id == current_user.id, 
                Subscription.tag_id == link.item_id
            )
        ).first()
         if not existing:
             sub = Subscription(
                 user_id=current_user.id,
                 tag_id=link.item_id
             )
             session.add(sub)
             
    elif link.item_type == ShortLinkType.EVENT:
        # "Add event to their calendar" -> This usually means reacting with Thumbs Up in this app context based on request?
        # Request: "If they add the event to their calendar then make them react with a thumbs up to the event."
        
        # Check permissions
        event = session.get(Event, link.item_id)
        if not event or not can_view_event(event, current_user, session):
             raise HTTPException(status_code=403, detail="Cannot access event")
             
        from app.models import EventReaction
        # Add reaction
        existing_reaction = session.exec(
            select(EventReaction).where(
                EventReaction.event_id == link.item_id,
                EventReaction.user_id == current_user.id,
                EventReaction.emoji == "👍" 
            )
        ).first()
        
        if not existing_reaction:
            reaction = EventReaction(
                event_id=link.item_id,
                user_id=current_user.id,
                emoji="👍"
            )
            session.add(reaction)
            
    session.commit()
    return {"message": "Success"}
