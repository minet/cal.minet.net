from fastapi import APIRouter, Depends, HTTPException, Body, BackgroundTasks
from sqlmodel import Session, select, and_, or_, col, func
from typing import List, Optional, Sequence, cast
from datetime import datetime, timezone
import os
from uuid import UUID
from app.database import get_session
from app.models import (
    Event, User, Membership, Role, Organization, EventVisibility, 
    Group, GroupMembership, EventTag, Tag, EventReaction, EventLink, EventGuestOrganization
)
from app.api.auth import get_current_user, get_current_user_optional
from app.schemas import (
    EventRead, CreateEvent, UpdateEvent, RejectEventRequest, Message, TagRead, OrganizationRead,
    ReactionSummary, ReactionDetail, UserPublicRead
)
from app.email.utils import send_email, render_email_template

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

    if event.end_time < datetime.now():
        return False
        
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
    
    # Enforce visibility flow
    if visibility in [EventVisibility.PUBLIC_APPROVED, EventVisibility.PUBLIC_REJECTED]:
        visibility = EventVisibility.PUBLIC_PENDING

    
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
        hide_details=event_data.hide_details,
        poster_url=event_data.poster_url
    )
    session.add(new_event)
    session.commit()
    session.refresh(new_event)
    
    # Add tags
    tags = []
    has_auto_approved = False
    for tag_id in event_data.tag_ids:
        tag_id = UUID(tag_id)
        tag = session.get(Tag, tag_id)
        if tag and str(tag.organization_id) == event_data.organization_id:
            event_tag = EventTag(event_id=new_event.id, tag_id=tag_id)
            session.add(event_tag)
            tags.append({
                "id": str(tag.id),
                "name": tag.name,
                "color": tag.color
            })
            if tag.is_auto_approved:
                has_auto_approved = True
                
    # Auto-approve if applicable
    if new_event.visibility == EventVisibility.PUBLIC_PENDING and has_auto_approved:
        new_event.visibility = EventVisibility.PUBLIC_APPROVED
        new_event.approved_at = datetime.now(timezone.utc)
        session.add(new_event)
        
    session.commit()
    
    # Add guest organizations
    for guest_org_id in event_data.guest_organization_ids:
        guest_org = session.get(Organization, UUID(guest_org_id))
        if guest_org:
            guest_link = EventGuestOrganization(event_id=new_event.id, organization_id=UUID(guest_org_id))
            session.add(guest_link)

    session.commit()
    session.refresh(new_event)
    
    session.refresh(new_event)
    
    return new_event.to_read_model(current_user, session)

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
    return [event.to_read_model(current_user, session) for event in drafts]

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
             visible_events.append(event.to_read_model(current_user, session))
    
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
    
    return [e.to_read_model(current_user, session) for e in all_events]
        

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
    
    return [e.to_read_model(current_user, session) for e in pending_events]

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
    
    return [e.to_read_model(current_user, session) for e in events]


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
    
    return event.to_read_model(current_user, session)

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
            event.visibility = EventVisibility(event_data.visibility)
            if not is_approved and event.visibility == EventVisibility.PUBLIC_APPROVED and not current_user.is_superadmin:
                event.visibility = EventVisibility.PUBLIC_PENDING
                event.approved_at = None
                event.rejection_message = None
            elif not is_approved and event.visibility == EventVisibility.PUBLIC_REJECTED and not current_user.is_superadmin:
                event.visibility = EventVisibility.PUBLIC_PENDING
                event.approved_at = None
                event.rejection_message = None                
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
        has_auto_approved = False
        for tag_id in event_data.tag_ids:
            tag = session.get(Tag, UUID(tag_id))
            if tag:
                session.add(EventTag(event_id=event.id, tag_id=UUID(tag_id)))
                if tag.is_auto_approved:
                    has_auto_approved = True
        
        # Check if we should auto-approve now
        if event.visibility == EventVisibility.PUBLIC_PENDING and has_auto_approved:
            event.visibility = EventVisibility.PUBLIC_APPROVED
            event.approved_at = datetime.utcnow()
            event.rejection_message = None

    elif event.visibility == EventVisibility.PUBLIC_PENDING:
         # Tags didn't change, but maybe visibility changed to pending. 
         # We need to check existing tags.
         existing_tags = session.exec(
             select(Tag).join(EventTag).where(EventTag.event_id == event.id)
         ).all()
         if any(t.is_auto_approved for t in existing_tags):
             event.visibility = EventVisibility.PUBLIC_APPROVED
             event.approved_at = datetime.utcnow()
             event.rejection_message = None

    
    # Update guest organizations
    if event_data.guest_organization_ids is not None:
        # Remove old guests
        old_guests = session.exec(
            select(EventGuestOrganization).where(EventGuestOrganization.event_id == event.id)
        ).all()
        for old_guest in old_guests:
            session.delete(old_guest)
            
        # Add new guests
        for guest_org_id in event_data.guest_organization_ids:
            guest_org = session.get(Organization, UUID(guest_org_id))
            if guest_org:
                guest_link = EventGuestOrganization(event_id=event.id, organization_id=UUID(guest_org_id))
                session.add(guest_link)
    
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

    # 4. Guest Organizations
    guests = session.exec(select(EventGuestOrganization).where(EventGuestOrganization.event_id == event.id)).all()
    for guest in guests:
        session.delete(guest)
    
    session.delete(event)
    session.commit()
    
    return {"message": "Event deleted successfully"}


@router.post("/{event_id}/approve", response_model=Message)
def approve_event(
    event_id: str,
    background_tasks: BackgroundTasks,
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
    event.approved_at = datetime.now(timezone.utc)
    event.rejection_message = None  # Clear any previous rejection
    
    session.add(event)
    session.commit()
    
    # Send email notification
    creator = session.get(User, event.created_by_id)
    if creator and creator.email:
        frontend_url = os.getenv("FRONTEND_URL", "https://cal.minet.net")
        event_url = f"{frontend_url}/events/{event.id}"
        
        html_content = render_email_template("event_approved.html", {
            "project_name": "Calend'INT",
            "user_name": creator.full_name or creator.email.split('@')[0],
            "event_title": event.title,
            "event_date": event.start_time.strftime("%d/%m/%Y à %H:%M"),
            "event_location": event.location or "Non spécifié",
            "event_url": event_url,
            "year" : datetime.now().year
        })
        
        background_tasks.add_task(
            send_email,
            email_to=creator.email,
            subject="Votre événement a été approuvé !",
            html_content=html_content
        )
    
    return {"message": "Event approved successfully"}


@router.post("/{event_id}/reject", response_model=Message)
def reject_event(
    event_id: str,
    request: RejectEventRequest,
    background_tasks: BackgroundTasks,
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
    
    # Send email notification
    creator = session.get(User, event.created_by_id)
    if creator and creator.email:
        frontend_url = os.getenv("FRONTEND_URL", "https://cal.minet.net")
        # Direct link to edit page might be better, but event detail has "Edit" button if owner
        event_url = f"{frontend_url}/events/{event.id}/edit"
        
        html_content = render_email_template("event_rejected.html", {
            "project_name": "Calend'INT",
            "user_name": creator.full_name or creator.email.split('@')[0],
            "event_title": event.title,
            "rejection_message": request.message,
            "event_url": event_url,
            "year": datetime.now().year
        })
        
        background_tasks.add_task(
            send_email,
            email_to=creator.email,
            subject="Votre événement a été refusé",
            html_content=html_content
        )
    
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
                user=user.to_public_read_model(),
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


@router.get("/{event_id}/overlapping", response_model=List[EventRead])
def get_overlapping_events(
    event_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get events that overlap with the user's event (Superadmin only for now as requested)"""
    if not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Superadmin access required")
    
    target_event = session.get(Event, UUID(event_id))
    if not target_event:
        raise HTTPException(status_code=404, detail="Event not found")
        
    # Find overlapping events:
    # (StartA <= EndB) and (EndA >= StartB)
    overlapping = session.exec(
        select(Event).where(
            Event.id != target_event.id,
            Event.start_time < target_event.end_time,
            Event.end_time > target_event.start_time,
            # We want both confirmed (APPROVED) and unconfirmed (PENDING)
            # Maybe restrict visibility if needed, but request said "unconfirmed or confirmed"
            Event.visibility.in_([EventVisibility.PUBLIC_APPROVED, EventVisibility.PUBLIC_PENDING]) #pyright: ignore
        )
    ).all()
    
    return [e.to_read_model(current_user, session) for e in overlapping]



