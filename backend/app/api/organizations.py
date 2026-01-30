from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, col
from typing import List, Optional
from app.database import get_session
from app.models import Organization, User, Membership, Role, EventVisibility
from app.api.auth import get_current_user, get_current_user_optional
from datetime import datetime, timezone
from app.schemas import OrganizationRead, EventRead

router = APIRouter()

@router.post("/", response_model=OrganizationRead)
def create_organization(
    org: Organization, 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
):
    # Check if user can create organizations
    if not current_user.is_superadmin:
        raise HTTPException(
            status_code=403, 
            detail="Only superadmins can create organizations"
        )
    
    session.add(org)
    session.commit()
    session.refresh(org)
    
    return org.to_read_model()

@router.get("/", response_model=List[OrganizationRead])
def list_organizations(session: Session = Depends(get_session)):
    orgs = session.exec(select(Organization)).all()
    return [o.to_read_model() for o in orgs]

@router.get("/{org_id}", response_model=OrganizationRead)
def get_organization(org_id: str, session: Session = Depends(get_session)):
    org = session.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org.to_read_model()

@router.get("/{org_id}/members")
def get_organization_members(org_id: str, session: Session = Depends(get_session)):
    """Get all members of an organization"""
    memberships = session.exec(
        select(Membership).where(Membership.organization_id == org_id)
    ).all()
    
    result = []
    for membership in memberships:
        user = session.get(User, membership.user_id)
        if user:
            result.append({
                "id": str(membership.id),
                "user_id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "role": membership.role
            })
    
    return result

from fastapi import APIRouter, Depends, HTTPException, Body

# ...

@router.post("/{org_id}/members")
def add_organization_member(
    org_id: str,
    email: str = Body(...),
    role: str = Body(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Add a member to an organization (requires org_admin or superadmin)"""
    # Check permissions
    if not current_user.is_superadmin:
        membership = session.exec(
            select(Membership).where(
                Membership.user_id == current_user.id,
                Membership.organization_id == org_id,
                Membership.role == Role.ORG_ADMIN # Changed to Role enum
            )
        ).first()
        
        if not membership:
            raise HTTPException(status_code=403, detail="Not authorized")
    
    # Find user by email
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if already member
    existing = session.exec(
        select(Membership).where(
            Membership.user_id == user.id,
            Membership.organization_id == org_id
        )
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="User is already a member")
    
    # Create membership
    try:
        role_enum = Role(role)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid role")

    new_membership = Membership(
        user_id=user.id,
        organization_id=org_id, # type: ignore
        role=role_enum
    )
    session.add(new_membership)
    session.commit()
    session.refresh(new_membership)
    
    return {"message": "Member added successfully", "membership_id": str(new_membership.id)}

@router.put("/{org_id}/members/{membership_id}")
def update_member_role(
    org_id: str,
    membership_id: str,
    role: Role, # Changed to Role enum
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update a member's role (requires org_admin or superadmin)"""
    # Check permissions
    if not current_user.is_superadmin:
        user_membership = session.exec(
            select(Membership).where(
                Membership.user_id == current_user.id,
                Membership.organization_id == org_id,
                Membership.role == Role.ORG_ADMIN # Changed to Role enum
            )
        ).first()
        
        if not user_membership:
            raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get membership to update
    membership = session.get(Membership, membership_id)
    if not membership or str(membership.organization_id) != org_id:
        raise HTTPException(status_code=404, detail="Membership not found")
    
    # Update role
    membership.role = role
    session.add(membership)
    session.commit()
    
    return {"message": "Role updated successfully"}

@router.delete("/{org_id}/members/{membership_id}")
def remove_organization_member(
    org_id: str,
    membership_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Remove a member from an organization (requires org_admin or superadmin)"""
    # Check permissions
    if not current_user.is_superadmin:
        user_membership = session.exec(
            select(Membership).where(
                Membership.user_id == current_user.id,
                Membership.organization_id == org_id,
                Membership.role == Role.ORG_ADMIN # Changed to Role enum
            )
        ).first()
        
        if not user_membership:
            raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get membership to delete
    membership = session.get(Membership, membership_id)
    if not membership or str(membership.organization_id) != org_id:
        raise HTTPException(status_code=404, detail="Membership not found")
    
    # Don't allow removing yourself if you're the last admin
    if membership.user_id == current_user.id and membership.role == Role.ORG_ADMIN: # Changed to Role enum
        admin_count = len(session.exec(
            select(Membership).where(
                Membership.organization_id == org_id,
                Membership.role == Role.ORG_ADMIN # Changed to Role enum
            )
        ).all())
        
        if admin_count <= 1:
            raise HTTPException(
                status_code=400, 
                detail="Cannot remove the last admin from the organization"
            )
    
    session.delete(membership)
    session.commit()
    
    return {"message": "Member removed successfully"}

@router.get("/{org_id}/events", response_model=List[EventRead])
def get_organization_events(
    org_id: str, 
    session: Session = Depends(get_session),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Get future events for an organization"""
    from app.models import Event
    
    events = session.exec(
        select(Event).where(
            Event.organization_id == org_id,
            Event.start_time >= datetime.now(timezone.utc),
            Event.visibility != EventVisibility.DRAFT
        ).order_by(col(Event.start_time))
    ).all()
    
    return [e.to_read_model(current_user, session) for e in events]

@router.get("/{org_id}/can-edit")
def can_edit_organization(
    org_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Check if current user can edit this organization"""
    if current_user.is_superadmin:
        return {"can_edit": True, "reason": "superadmin"}
    
    # Check if user is ORG_ADMIN of this organization
    membership = session.exec(
        select(Membership).where(
            Membership.user_id == current_user.id,
            Membership.organization_id == org_id,
            Membership.role == Role.ORG_ADMIN
        )
    ).first()
    
    if membership:
        return {"can_edit": True, "reason": "org_admin"}
    
    # Check if user is ORG_ADMIN of parent organization
    org = session.get(Organization, org_id)
    if org and org.parent_id:
        parent_membership = session.exec(
            select(Membership).where(
                Membership.user_id == current_user.id,
                Membership.organization_id == org.parent_id,
                Membership.role == Role.ORG_ADMIN
            )
        ).first()
        
        if parent_membership:
            return {"can_edit": True, "reason": "parent_admin"}
    
    return {"can_edit": False, "reason": "no_permission"}


@router.put("/{org_id}", response_model=Organization)
def update_organization(
    org_id: str,
    org_update: Organization,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update an organization (requires permission)"""
    org = session.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Check permissions
    can_edit = can_edit_organization(org_id, current_user, session)
    if not can_edit["can_edit"]:
        raise HTTPException(status_code=403, detail="Not authorized to edit this organization")
    
    # Update fields
    org.name = org_update.name
    org.slug = org_update.slug
    org.description = org_update.description
    org.logo_url = org_update.logo_url
    org.type = org_update.type
    org.parent_id = org_update.parent_id
    org.color_primary = org_update.color_primary
    org.color_secondary = org_update.color_secondary
    org.color_dark = org_update.color_dark
    
    from datetime import datetime
    org.updated_at = datetime.now(timezone.utc)
    
    session.add(org)
    session.commit()
    session.refresh(org)
    
    return org

@router.delete("/{org_id}")
def delete_organization(
    org_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete an organization and all its related entities (requires permission)"""
    from app.models import (
        Membership, Subscription, Tag, OrganizationLink, 
        Group, GroupMembership, Event, EventLink, EventTag, 
        EventReaction, EventGuestOrganization
    )
    from app.services.storage import delete_file
    
    org = session.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Check permissions (same as edit, effectively ORG_ADMIN or SUPERADMIN)
    can_edit = can_edit_organization(org_id, current_user, session)
    if not can_edit["can_edit"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete this organization")
    
    # 1. Delete Memberships
    memberships = session.exec(select(Membership).where(Membership.organization_id == org_id)).all()
    for m in memberships:
        session.delete(m)
        
    # 2. Delete Subscriptions
    subscriptions = session.exec(select(Subscription).where(Subscription.organization_id == org_id)).all()
    for s in subscriptions:
        session.delete(s)
        
    # 3. Delete OrganizationLinks
    links = session.exec(select(OrganizationLink).where(OrganizationLink.organization_id == org_id)).all()
    for l in links:
        session.delete(l)
        
    # 4. Delete Tags and their dependencies
    tags = session.exec(select(Tag).where(Tag.organization_id == org_id)).all()
    for tag in tags:
        # Delete Tag Subscriptions
        tag_subs = session.exec(select(Subscription).where(Subscription.tag_id == tag.id)).all()
        for ts in tag_subs:
            session.delete(ts)
            
        # Delete EventTags for this tag
        event_tags = session.exec(select(EventTag).where(EventTag.tag_id == tag.id)).all()
        for et in event_tags:
            session.delete(et)
            
        session.delete(tag)
        
    # 5. Delete Groups and their dependencies
    groups = session.exec(select(Group).where(Group.organization_id == org_id)).all()
    for group in groups:
        # Delete Group Memberships
        group_members = session.exec(select(GroupMembership).where(GroupMembership.group_id == group.id)).all()
        for gm in group_members:
            session.delete(gm)
            
        # Note: Events related to Group are also related to Organization, so they will be handled in Events section
        
        session.delete(group)
        
    # 6. Delete Events and their dependencies
    events = session.exec(select(Event).where(Event.organization_id == org_id)).all()
    for event in events:
        # Delete Event Links
        event_links = session.exec(select(EventLink).where(EventLink.event_id == event.id)).all()
        for el in event_links:
            session.delete(el)
            
        # Delete Event Tags
        event_tags_remaining = session.exec(select(EventTag).where(EventTag.event_id == event.id)).all()
        for et in event_tags_remaining:
            session.delete(et)
            
        # Delete Event Reactions
        reactions = session.exec(select(EventReaction).where(EventReaction.event_id == event.id)).all()
        for r in reactions:
            session.delete(r)
            
        # Delete Event Guest Organizations (where this event is the host)
        guest_orgs = session.exec(select(EventGuestOrganization).where(EventGuestOrganization.event_id == event.id)).all()
        for go in guest_orgs:
            session.delete(go)

        # Delete Event Poster
        if event.poster_url and event.poster_url.startswith("/uploads/"):
            filename = event.poster_url.replace("/uploads/", "")
            delete_file(filename)
            
        session.delete(event)
        
    # 7. Clean up Guest Events (where this org is a guest)
    guest_entries = session.exec(select(EventGuestOrganization).where(EventGuestOrganization.organization_id == org_id)).all()
    for ge in guest_entries:
        session.delete(ge)
        
    # 8. Unlink Children (set parent_id to None)
    children = session.exec(select(Organization).where(Organization.parent_id == org_id)).all()
    for child in children:
        child.parent_id = None
        session.add(child)
        
    # 9. Delete Organization and Logo
    if org.logo_url and org.logo_url.startswith("/uploads/"):
        filename = org.logo_url.replace("/uploads/", "")
        delete_file(filename)
        
    session.delete(org)
    
    session.commit()
    
    return {"message": "Organization and all related data deleted successfully"}


