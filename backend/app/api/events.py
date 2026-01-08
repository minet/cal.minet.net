from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session, select, and_, or_, col, func
from typing import List, Optional, Sequence, cast
from datetime import datetime
from uuid import UUID
from app.database import get_session
from app.models import (
    Event, User, Membership, Role, Organization, EventVisibility, 
    Group, GroupMembership, EventTag, Tag, EventReaction, EventLink
)
from app.api.auth import get_current_user, get_current_user_optional
from app.schemas import (
    EventRead, CreateEvent, UpdateEvent, RejectEventRequest, Message, TagRead, OrganizationRead,
    ReactionSummary, ReactionDetail, UserPublicRead
)

router = APIRouter()

def get_org_membership(user: User, org_id, session: Session) -> Optional[Membership]:
    """Get membership for user in organization"""
    if not user:
        return None
    return session.exec(
        select(Membership).where(
            Membership.user_id == user.id,
            Membership.organization_id == org_id
        )
    ).first()

def can_view_event(event: Event, user: Optional[User], session: Session) -> bool:
    """Check if user can view an event based on visibility"""
    
    # PUBLIC_APPROVED: anyone can see
    if event.visibility == EventVisibility.PUBLIC_APPROVED:
        return True

    if not user:
        return False
        
    membership = get_org_membership(user, event.organization_id, session)
    is_super = user.is_superadmin
    is_admin = is_super or (membership and membership.role == Role.ORG_ADMIN)
    is_member = membership and membership.role in [Role.ORG_ADMIN, Role.ORG_MEMBER]
    is_in_org = membership is not None

    # DRAFT: only org members (any role)
    if event.visibility == EventVisibility.DRAFT:
        return is_super or is_in_org
    
    # PRIVATE: group members, author, or admins
    elif event.visibility == EventVisibility.PRIVATE:
        if event.created_by_id == user.id:
            return True
            
        if is_admin:
            return True
            
        if event.group_id:
            group_membership = session.exec(
                select(GroupMembership).where(
                    GroupMembership.group_id == event.group_id,
                    GroupMembership.user_id == user.id
                )
            ).first()
            if group_membership:
                return True
        
        return False
    
    # PUBLIC_PENDING / REJECTED: org members (any role)
    elif event.visibility in [EventVisibility.PUBLIC_PENDING, EventVisibility.PUBLIC_REJECTED]:
        return is_super or is_in_org
    
    return False

def can_edit_event(event: Event, user: User, session: Session) -> bool:
    """Check if user can edit an event"""
    if user.is_superadmin:
        return True
        
    if event.created_by_id == user.id:
        return True
        
    membership = get_org_membership(user, event.organization_id, session)
    if not membership:
        return False
        
    # Org Admins can edit everything
    if membership.role == Role.ORG_ADMIN:
        return True
        
    # Org Members can edit everything EXCEPT Private (unless author, handled above)
    if membership.role == Role.ORG_MEMBER:
        return event.visibility != EventVisibility.PRIVATE
        
    # Viewers (or others) cannot edit
    return False

@router.post("/", response_model=EventRead)
def create_event(
    event_data: CreateEvent,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Create a new event"""
    # Validate visibility
    try:
        visibility = EventVisibility(event_data.visibility)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid visibility value")
    
    # If private, group_id is required
    if visibility == EventVisibility.PRIVATE and not event_data.group_id:
        raise HTTPException(status_code=400, detail="group_id required for private events")
    
    # Verify group exists and belongs to organization if provided
    if event_data.group_id:
        group = session.get(Group, UUID(event_data.group_id))
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        if str(group.organization_id) != event_data.organization_id:
            raise HTTPException(status_code=400, detail="Group does not belong to this organization")
            
    # Check permissions
    if not current_user.is_superadmin:
        membership = get_org_membership(current_user, UUID(event_data.organization_id), session)
        if not membership or membership.role not in [Role.ORG_ADMIN, Role.ORG_MEMBER]:
            raise HTTPException(status_code=403, detail="Not authorized to create events")
    
    # Create event
    new_event = Event(
        title=event_data.title,
        description=event_data.description,
        start_time=event_data.start_time,
        end_time=event_data.end_time,
        location=event_data.location,
        location_url=event_data.location_url,
        organization_id=UUID(event_data.organization_id),
        visibility=visibility,
        group_id=UUID(event_data.group_id) if event_data.group_id else None,
        created_by_id=current_user.id,
        show_on_schedule=event_data.show_on_schedule,
        hide_details=event_data.hide_details
    )
    session.add(new_event)
    session.commit()
    session.refresh(new_event)
    
    # Add tags
    tags = []
    for tag_id in event_data.tag_ids:
        tag = session.get(Tag, UUID(tag_id))
        if tag and str(tag.organization_id) == event_data.organization_id:
            event_tag = EventTag(event_id=new_event.id, tag_id=UUID(tag_id))
            session.add(event_tag)
            tags.append({
                "id": str(tag.id),
                "name": tag.name,
                "color": tag.color
            })
    session.commit()
    
    # Load organization
    organization = session.get(Organization, new_event.organization_id)

    return {
        "id": str(new_event.id),
        "title": new_event.title,
        "description": new_event.description,
        "start_time": new_event.start_time,
        "end_time": new_event.end_time,
        "location": new_event.location,
        "location_url": new_event.location_url,
        "visibility": new_event.visibility,
        "show_on_schedule": new_event.show_on_schedule,
        "hide_details": new_event.hide_details,
        "poster_url": new_event.poster_url,
        "created_at": new_event.created_at,
        "organization": organization,
        "tags": tags,
        "created_by_id": str(new_event.created_by_id)
    }

@router.get("/drafts", response_model=List[EventRead])
def list_drafts(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get all draft events visible to the user"""
    # Get drafts created by user
    user_drafts = session.exec(
        select(Event).where(
            Event.visibility == EventVisibility.DRAFT,
            Event.created_by_id == current_user.id
        )
    ).all()
    user_drafts = cast(List[Event], user_drafts)
    
    # Get drafts from organizations where user is admin
    admin_memberships = session.exec(
        select(Membership).where(
            Membership.user_id == current_user.id,
            Membership.role == Role.ORG_ADMIN
        )
    ).all()
    
    org_ids = [m.organization_id for m in admin_memberships]
    
    org_drafts: List[Event] = []
    if org_ids:
        org_drafts = session.exec(
            select(Event).where(
                Event.visibility == EventVisibility.DRAFT,
                Event.organization_id.in_(org_ids), #pyright: ignore
                Event.created_by_id != current_user.id # Avoid duplicates
            )
        ).all()
    
    drafts = user_drafts + org_drafts
    
    # Format response
    result = []
    for event in drafts:
        # Load organization
        event.organization = session.get(Organization, event.organization_id)
        
        # Load tags
        event_tags = session.exec(
            select(EventTag).where(EventTag.event_id == event.id)
        ).all()
        tags = []
        for et in event_tags:
            tag = session.get(Tag, et.tag_id)
            if tag:
                tags.append({
                    "id": str(tag.id),
                    "name": tag.name,
                    "color": tag.color
                })
        
        result.append({
            "id": str(event.id),
            "title": event.title,
            "description": event.description,
            "start_time": event.start_time.isoformat(),
            "end_time": event.end_time.isoformat(),
            "location": event.location,
            "location_url": event.location_url,
            "visibility": event.visibility.value,
            "show_on_schedule": event.show_on_schedule,
            "poster_url": event.poster_url,
            "organization": {
                "id": str(event.organization.id),
                "name": event.organization.name,
                "logo_url": event.organization.logo_url,
                "color_chroma": event.organization.color_chroma,
                "color_hue": event.organization.color_hue,
            } if event.organization else None,
            "tags": tags,
            "is_draft": True, # Helper for frontend
            "created_at": event.created_at.isoformat()
        })
        
    return result

@router.get("/", response_model=List[EventRead])
def list_events(
    current_user: Optional[User] = Depends(get_current_user_optional),
    session: Session = Depends(get_session)
):
    """Get all events visible to the user"""
    all_events = session.exec(select(Event)).all()
    
    visible_events = []
    for event in all_events:

        if can_view_event(event, current_user, session) or event.show_on_schedule:
            # Load organization
            event.organization = session.get(Organization, event.organization_id)
            
            # Load tags
            event_tags = session.exec(
                select(EventTag).where(EventTag.event_id == event.id)
            ).all()
            tags = []
            for et in event_tags:
                tag = session.get(Tag, et.tag_id)
                if tag:
                    tags.append({
                        "id": str(tag.id),
                        "name": tag.name,
                        "color": tag.color
                    })
            
            # Check if we should hide details for this user
            should_hide = False
            if event.hide_details and event.visibility == EventVisibility.PUBLIC_APPROVED:
                # Hide details for non-org members
                is_auth = False
                if current_user:
                    if current_user.is_superadmin:
                        is_auth = True
                    elif get_org_membership(current_user, event.organization_id, session):
                        is_auth = True
                
                if not is_auth:
                    should_hide = True
            
            # Load reactions
            reactions = get_event_reactions_summary(event.id, current_user.id if current_user else None, session)
            
            visible_events.append({
                "id": str(event.id),
                "title": event.title,
                "description": None if should_hide else event.description,
                "start_time": event.start_time.isoformat(),
                "end_time": event.end_time.isoformat(),
                "location": None if should_hide else event.location,
                "location_url": None if should_hide else event.location_url,
                "visibility": event.visibility.value,
                "hide_details": event.hide_details,
                "show_on_schedule": event.show_on_schedule,
                "poster_url": None if should_hide else event.poster_url,
                "organization": {
                    "id": str(event.organization.id),
                    "name": event.organization.name,
                    "logo_url": event.organization.logo_url,
                    "color_chroma": event.organization.color_chroma,
                    "color_hue": event.organization.color_hue,
                } if event.organization else None,
                "tags": tags,
                "created_at": event.created_at.isoformat(),
                "reactions": reactions
            })
    
    return visible_events

@router.get("/my-events", response_model=List[EventRead])
def list_my_events(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get events the user can manage (created by user or in orgs they admin)"""
    # Combine queries using a join to find events where user is creator OR admin of org
    query = (
        select(Event)
        .distinct()
        .outerjoin(
            Membership,
            and_(
                Membership.organization_id == Event.organization_id,
                Membership.user_id == current_user.id,
                Membership.role.in_([Role.ORG_ADMIN, Role.ORG_MEMBER]) #pyright: ignore
            )
        )
        .where(
            Membership.id.is_not(None) #pyright: ignore
        )
    )
    
    all_events = session.exec(query).all()
    
    result = []
    for event in all_events:
        event.organization = session.get(Organization, event.organization_id)
        if not event.organization:
            continue
        
        # Load tags
        event_tags = session.exec(
            select(EventTag).where(EventTag.event_id == event.id)
        ).all()
        tags = []
        for et in event_tags:
            tag = session.get(Tag, et.tag_id)
            if tag:
                tags.append({
                    "id": str(tag.id),
                    "name": tag.name,
                    "color": tag.color
                })

        # Load reactions
        reactions = get_event_reactions_summary(event.id, current_user.id, session)

        result.append({
            "id": str(event.id),
            "title": event.title,
            "description": event.description,
            "start_time": event.start_time.isoformat(),
            "end_time": event.end_time.isoformat(),
            "location": event.location,
            "location_url": event.location_url,
            "organization": {
                "id": str(event.organization_id),
                "name": event.organization.name,
                "slug": event.organization.slug,
                "description": event.organization.description,
                "logo_url": event.organization.logo_url,
                "type": event.organization.type,
                "parent_id": str(event.organization.parent_id) if event.organization.parent_id else None,
                "created_at": event.organization.created_at.isoformat(),
                "updated_at": event.organization.updated_at.isoformat(),
                "color_chroma": event.organization.color_chroma,
                "color_hue": event.organization.color_hue
            },
            "visibility": event.visibility,
            "group_id": str(event.group_id) if event.group_id else None,
            "tags": tags,
            "created_at": event.created_at.isoformat(),
            "reactions": reactions
        })
    
    return result
        

@router.get("/pending-approvals", response_model=List[EventRead])
def list_pending_approvals(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get all events pending approval (superadmin only)"""
    if not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Superadmin access required")
    
    pending_events = session.exec(
        select(Event).where(Event.visibility == EventVisibility.PUBLIC_PENDING)
    ).all()
    
    result = []
    for event in pending_events:
        event.organization = session.get(Organization, event.organization_id)
        creator = session.get(User, event.created_by_id)
        
        result.append({
            "id": str(event.id),
            "title": event.title,
            "description": event.description,
            "start_time": event.start_time.isoformat(),
            "end_time": event.end_time.isoformat(),
            "location": event.location,
            "created_at": event.created_at.isoformat(),
            "organization": {
                "id": str(event.organization.id),
                "name": event.organization.name,
                "name": event.organization.name,
                "logo_url": event.organization.logo_url,
                "color_chroma": event.organization.color_chroma,
                "color_hue": event.organization.color_hue,
            } if event.organization else None,
            "created_by": {
                "id": str(creator.id),
                "full_name": creator.full_name,
                "email": creator.email
            } if creator else None,
            "visibility": event.visibility.value,
            "created_at": event.created_at.isoformat()
        })
    
    return result

@router.get("/processed-approvals", response_model=List[EventRead])
def list_processed_approvals(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get recently processed stats (approved or rejected) - Superadmin only"""
    if not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Superadmin access required")
    
    # Get approved or rejected events
    # We limit to 50 for performance
    events = session.exec(
        select(Event)
        .where(Event.visibility.in_([ #pyright: ignore
            EventVisibility.PUBLIC_APPROVED, 
            EventVisibility.PUBLIC_REJECTED
        ]))
        .order_by(Event.start_time.desc()) #pyright: ignore
        .limit(50)
    ).all()
    
    result = []
    for event in events:
        event.organization = session.get(Organization, event.organization_id)
        creator = session.get(User, event.created_by_id)
        
        result.append({
            "id": str(event.id),
            "title": event.title,
            "description": event.description,
            "start_time": event.start_time.isoformat(),
            "end_time": event.end_time.isoformat(),
            "location": event.location,
            "visibility": event.visibility.value,
            "rejection_message": event.rejection_message,
            "approved_at": event.approved_at.isoformat() if event.approved_at else None,
            "organization": {
                "id": str(event.organization.id),
                "name": event.organization.name,
                "name": event.organization.name,
                "logo_url": event.organization.logo_url,
                "color_chroma": event.organization.color_chroma,
                "color_hue": event.organization.color_hue,
            } if event.organization else None,
            "created_by": {
                "id": str(creator.id),
                "full_name": creator.full_name,
                "email": creator.email
            } if creator else None,
            "created_at": event.created_at.isoformat()
        })
    
    return result


@router.post("/{event_id}/reset-status", response_model=Message)
def reset_event_status(
    event_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Reset event status to pending (Superadmin only)"""
    if not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Superadmin access required")
    
    event = session.get(Event, UUID(event_id))
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Only allow resetting from APPROVED or REJECTED
    if event.visibility not in [EventVisibility.PUBLIC_APPROVED, EventVisibility.PUBLIC_REJECTED]:
        raise HTTPException(status_code=400, detail="Event is not processed")
    
    event.visibility = EventVisibility.PUBLIC_PENDING
    event.rejection_message = None
    event.approved_at = None
    
    session.add(event)
    session.commit()
    
    return {"message": "Event status reset to pending"}

def get_event_reactions_summary(event_id: UUID, current_user_id: Optional[UUID], session: Session) -> List[ReactionSummary]:
    """Helper to calculate reaction summaries for an event"""
    # Group by emoji
    results = session.exec(
        select(EventReaction.emoji, func.count(EventReaction.id)) #pyright: ignore
        .where(EventReaction.event_id == event_id)
        .group_by(EventReaction.emoji)
    ).all()
    
    # Check what user reacted with
    user_emojis = set()
    if current_user_id:
        user_reactions = session.exec(
            select(EventReaction.emoji).where(
                EventReaction.event_id == event_id,
                EventReaction.user_id == current_user_id
            )
        ).all()
        user_emojis = set(user_reactions)

    summary = []
    for emoji, count in results:
        summary.append(ReactionSummary(
            emoji=emoji,
            count=count,
            user_reacted=emoji in user_emojis
        ))
    
    return summary

@router.get("/{event_id}", response_model=EventRead)
def get_event(
    event_id: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    session: Session = Depends(get_session)
):
    """Get a single event"""
    event = session.get(Event, UUID(event_id))
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check visibility
    if not can_view_event(event, current_user, session) and not event.show_on_schedule:
        raise HTTPException(status_code=403, detail="Not authorized to view this event")
    
    # Load organization
    event.organization = session.get(Organization, event.organization_id)
    
    # Load group if private
    group_info = None
    if event.group_id:
        group = session.get(Group, event.group_id)
        if group:
            group_info = {
                "id": str(group.id),
                "name": group.name
            }
    
    # Load tags
    event_tags = session.exec(
        select(EventTag).where(EventTag.event_id == event.id)
    ).all()
    tags = []
    for et in event_tags:
        tag = session.get(Tag, et.tag_id)
        if tag:
            tags.append({
                "id": str(tag.id),
                "name": tag.name,
                "color": tag.color
            })
            
    # Load reactions
    reactions = get_event_reactions_summary(event.id, current_user.id if current_user else None, session)
    
    # Check if we should hide details for this user
    should_hide = False
    if event.hide_details and event.visibility == EventVisibility.PUBLIC_APPROVED:
        is_authorized = False
        if current_user:
            if current_user.is_superadmin:
                is_authorized = True
            else:
                membership = get_org_membership(current_user, event.organization_id, session)
                if membership:
                    is_authorized = True
        
        if not is_authorized:
            should_hide = True
    
    return {
        "id": str(event.id),
        "title": event.title,
        "description": None if should_hide else event.description,
        "start_time": event.start_time.isoformat(),
        "end_time": event.end_time.isoformat(),
        "location": None if should_hide else event.location,
        "location_url": None if should_hide else event.location_url,
        "visibility": event.visibility.value,
        "hide_details": event.hide_details,
        "rejection_message": event.rejection_message,
        "approved_at": event.approved_at.isoformat() if event.approved_at else None,
        "show_on_schedule": event.show_on_schedule,
        "group": group_info,
        "poster_url": None if should_hide else event.poster_url,
        "organization": {
            "id": str(event.organization.id),
            "name": event.organization.name,
            "logo_url": event.organization.logo_url,
            "type": event.organization.type.value,
            "color_chroma": event.organization.color_chroma,
            "color_hue": event.organization.color_hue,
        } if event.organization else None,
        "tags": tags,
        "created_by_id": str(event.created_by_id),
        "created_at": event.created_at.isoformat(),
        "reactions": reactions
    }

@router.put("/{event_id}", response_model=Message)
def update_event(
    event_id: str,
    event_data: UpdateEvent,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update an event"""
    event = session.get(Event, UUID(event_id))
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check permissions
    if not can_edit_event(event, current_user, session):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Lock date/time editing for approved events (unless superadmin)
    is_approved = event.visibility == EventVisibility.PUBLIC_APPROVED
    if is_approved and not current_user.is_superadmin:
        if event_data.start_time is not None or event_data.end_time is not None:
            
            # Put the event back into the pending state
            event.visibility = EventVisibility.PUBLIC_PENDING
    
    # Update fields
    if event_data.title is not None:
        event.title = event_data.title
    if event_data.description is not None:
        event.description = event_data.description
    if event_data.start_time is not None:
        event.start_time = event_data.start_time
    if event_data.end_time is not None:
        event.end_time = event_data.end_time
    if event_data.location is not None:
        event.location = event_data.location
    if event_data.location_url is not None:
        event.location_url = event_data.location_url
    if event_data.visibility is not None:
        try:
            new_visibility = EventVisibility(event_data.visibility)
            # Prevent changing approved events to non-approved states (unless superadmin)
            if is_approved and new_visibility != EventVisibility.PUBLIC_APPROVED and not current_user.is_superadmin:
                raise HTTPException(
                    status_code=400, 
                    detail="Cannot change visibility of approved events"
                )
            event.visibility = new_visibility
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid visibility value")
    if event_data.group_id is not None:
        event.group_id = UUID(event_data.group_id) if event_data.group_id else None
    if event_data.show_on_schedule is not None:
        event.show_on_schedule = event_data.show_on_schedule
    if event_data.poster_url is not None:
        event.poster_url = event_data.poster_url
    if event_data.hide_details is not None:
        event.hide_details = event_data.hide_details
    
    # Update tags
    if event_data.tag_ids is not None:
        # Remove old tags
        old_tags = session.exec(
            select(EventTag).where(EventTag.event_id == event.id)
        ).all()
        for old_tag in old_tags:
            session.delete(old_tag)
        
        # Add new tags
        for tag_id in event_data.tag_ids:
            tag = session.get(Tag, UUID(tag_id))
            if tag and tag.organization_id == event.organization_id:
                event_tag = EventTag(event_id=event.id, tag_id=UUID(tag_id))
                session.add(event_tag)
    
    session.add(event)
    session.commit()
    session.refresh(event)
    
    return {"message": "Event updated successfully"}

@router.delete("/{event_id}", response_model=Message)
def delete_event(
    event_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete an event"""
    event = session.get(Event, UUID(event_id))
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check permissions
    if not can_edit_event(event, current_user, session):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Manually delete dependent entities to ensure no foreign key constraints are violated
    # 1. Links
    links = session.exec(select(EventLink).where(EventLink.event_id == event.id)).all()
    for link in links:
        session.delete(link)
        
    # 2. Tags
    tags = session.exec(select(EventTag).where(EventTag.event_id == event.id)).all()
    for tag in tags:
        session.delete(tag)
        
    # 3. Reactions
    reactions = session.exec(select(EventReaction).where(EventReaction.event_id == event.id)).all()
    for reaction in reactions:
        session.delete(reaction)
    
    session.delete(event)
    session.commit()
    
    return {"message": "Event deleted successfully"}


@router.post("/{event_id}/approve", response_model=Message)
def approve_event(
    event_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Approve an event (superadmin only)"""
    if not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Superadmin access required")
    
    event = session.get(Event, UUID(event_id))
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    if event.visibility != EventVisibility.PUBLIC_PENDING:
        raise HTTPException(status_code=400, detail="Event is not pending approval")
    
    event.visibility = EventVisibility.PUBLIC_APPROVED
    event.approved_at = datetime.utcnow()
    event.rejection_message = None  # Clear any previous rejection
    
    session.add(event)
    session.commit()
    
    return {"message": "Event approved successfully"}


@router.post("/{event_id}/reject", response_model=Message)
def reject_event(
    event_id: str,
    request: RejectEventRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Reject an event (superadmin only)"""
    if not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Superadmin access required")
    
    event = session.get(Event, UUID(event_id))
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    if event.visibility != EventVisibility.PUBLIC_PENDING:
        raise HTTPException(status_code=400, detail="Event is not pending approval")
    
    event.visibility = EventVisibility.PUBLIC_REJECTED
    event.rejection_message = request.message
    
    session.add(event)
    session.commit()
    
    return {"message": "Event rejected"}


@router.post("/{event_id}/submit-for-approval", response_model=Message)
def submit_for_approval(
    event_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Submit an event for approval (changes draft to public_pending)"""
    event = session.get(Event, UUID(event_id))
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check if user can edit
    if not can_edit_event(event, current_user, session):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if event.visibility not in [EventVisibility.DRAFT, EventVisibility.PUBLIC_REJECTED]:
        raise HTTPException(
            status_code=400, 
            detail="Can only submit draft or rejected events for approval"
        )
    
    event.visibility = EventVisibility.PUBLIC_PENDING
    event.rejection_message = None  # Clear rejection message
    
    session.add(event)
    session.commit()
    
    return {"message": "Event submitted for approval"}


@router.post("/{event_id}/react", response_model=Message)
def toggle_reaction(
    event_id: str,
    reaction_data: dict = Body(...), # Expect { "emoji": "👍" }
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Toggle reaction on an event"""
    event = session.get(Event, UUID(event_id))
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check visibility
    if not can_view_event(event, current_user, session):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    emoji = reaction_data.get("emoji")
    if not emoji:
        raise HTTPException(status_code=400, detail="Emoji required")
    
    # Check if user already reacted
    existing_reaction = session.exec(
        select(EventReaction).where(
            EventReaction.event_id == UUID(event_id),
            EventReaction.user_id == current_user.id
        )
    ).first()
    
    if existing_reaction:
        if existing_reaction.emoji == emoji:
            # Remove reaction if same emoji
            session.delete(existing_reaction)
            session.commit()
            return {"message": "Reaction removed"}
        else:
            # Update emoji if different
            existing_reaction.emoji = emoji
            session.add(existing_reaction)
            session.commit()
            return {"message": "Reaction updated"}
    else:
        # Create new reaction
        new_reaction = EventReaction(
            event_id=UUID(event_id),
            user_id=current_user.id,
            emoji=emoji
        )
        session.add(new_reaction)
        session.commit()
        return {"message": "Reaction added"}

@router.get("/{event_id}/reactions", response_model=List[ReactionDetail])
def list_reactions(
    event_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """List detailed reactions for an event (admin/manager only)"""
    event = session.get(Event, UUID(event_id))
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check edit permissions (usually implies admin/manager)
    if not can_edit_event(event, current_user, session):
        raise HTTPException(status_code=403, detail="Not authorized to view reaction details")
    
    reactions = session.exec(
        select(EventReaction).where(EventReaction.event_id == UUID(event_id))
    ).all()
    
    result = []
    for r in reactions:
        user = session.get(User, r.user_id)
        if user:
            result.append(ReactionDetail(
                user=UserPublicRead(
                    id=user.id,
                    email=user.email,
                    full_name=user.full_name,
                    profile_picture_url=user.profile_picture_url
                ),
                emoji=r.emoji,
                created_at=r.created_at
            ))
    
    return result

@router.delete("/{event_id}/reactions/{user_id}", response_model=Message)
def delete_user_reaction(
    event_id: str,
    user_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete a specific user's reaction (admin only)"""
    event = session.get(Event, UUID(event_id))
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check edit permissions
    if not can_edit_event(event, current_user, session):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    reaction = session.exec(
        select(EventReaction).where(
            EventReaction.event_id == UUID(event_id),
            EventReaction.user_id == UUID(user_id)
        )
    ).first()
    
    if not reaction:
        raise HTTPException(status_code=404, detail="Reaction not found")
    
    session.delete(reaction)
    session.commit()
    
    return {"message": "Reaction deleted"}



