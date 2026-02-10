from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app.api.auth import get_current_user
from app.database import get_session
from app.models import Group, GroupMembership, Membership, Organization, Role, User, Event

router = APIRouter()

# Request models
class GroupCreate(BaseModel):
    name: str
    description: Optional[str] = None

class GroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class GroupMemberAdd(BaseModel):
    user_email: str

# Helper function to check if user is admin of organization
def check_org_admin(user: User, org_id: str, session: Session) -> bool:
    if user.is_superadmin:
        return True
    
    membership = session.exec(
        select(Membership).where(
            Membership.user_id == user.id,
            Membership.organization_id == UUID(org_id),
            Membership.role == Role.ORG_ADMIN
        )
    ).first()
    
    return membership is not None

@router.get("/organizations/{org_id}/groups")
def get_organization_groups(
    org_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get all groups for an organization"""
    # Verify organization exists
    org = session.get(Organization, UUID(org_id))
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Get groups
    groups = session.exec(
        select(Group).where(Group.organization_id == UUID(org_id))
    ).all()
    
    # Return groups with member count
    result = []
    for group in groups:
        member_count = len(session.exec(
            select(GroupMembership).where(GroupMembership.group_id == group.id)
        ).all())
        
        result.append({
            "id": str(group.id),
            "name": group.name,
            "description": group.description,
            "member_count": member_count,
            "created_at": group.created_at.isoformat()
        })
    
    return result

@router.post("/organizations/{org_id}/groups")
def create_group(
    org_id: str,
    group_data: GroupCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Create a new group (org_admin only)"""
    # Check permissions
    if not check_org_admin(current_user, org_id, session):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Verify organization exists
    org = session.get(Organization, UUID(org_id))
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Create group
    group = Group(
        name=group_data.name,
        description=group_data.description,
        organization_id=UUID(org_id)
    )
    session.add(group)
    session.commit()
    session.refresh(group)
    
    return {
        "id": str(group.id),
        "name": group.name,
        "description": group.description,
        "created_at": group.created_at.isoformat()
    }

@router.put("/groups/{group_id}")
def update_group(
    group_id: str,
    group_data: GroupUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update a group (org_admin only)"""
    # Get group
    group = session.get(Group, UUID(group_id))
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Check permissions
    if not check_org_admin(current_user, str(group.organization_id), session):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Update fields
    if group_data.name is not None:
        group.name = group_data.name
    if group_data.description is not None:
        group.description = group_data.description
    
    session.add(group)
    session.commit()
    session.refresh(group)
    
    return {
        "id": str(group.id),
        "name": group.name,
        "description": group.description
    }

@router.delete("/groups/{group_id}")
def delete_group(
    group_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete a group (org_admin only)"""
    # Get group
    group = session.get(Group, UUID(group_id))
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Check permissions
    if not check_org_admin(current_user, str(group.organization_id), session):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Delete memberships
    memberships = session.exec(
        select(GroupMembership).where(GroupMembership.group_id == UUID(group_id))
    ).all()
    for membership in memberships:
        session.delete(membership)
    session.commit()

    # Change the group_id of events to null
    events = session.exec(
        select(Event).where(Event.group_id == UUID(group_id))
    ).all()
    for event in events:
        event.group_id = None
        session.add(event)
    session.commit()

    # Delete group
    session.delete(group)
    session.commit()
    
    return {"message": "Group deleted successfully"}

@router.get("/groups/{group_id}/members")
def get_group_members(
    group_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get all members of a group"""
    # Get group
    group = session.get(Group, UUID(group_id))
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Get memberships with user details
    memberships = session.exec(
        select(GroupMembership).where(GroupMembership.group_id == UUID(group_id))
    ).all()
    
    result = []
    for membership in memberships:
        user = session.get(User, membership.user_id)
        if user:
            result.append({
                "membership_id": str(membership.id),
                "user_id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "joined_at": membership.joined_at.isoformat()
            })
    
    return result

@router.post("/groups/{group_id}/members")
def add_group_member(
    group_id: str,
    member_data: GroupMemberAdd,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Add a member to a group (org_admin only)"""
    # Get group
    group = session.get(Group, UUID(group_id))
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Check permissions
    if not check_org_admin(current_user, str(group.organization_id), session):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Find user by email
    user = session.exec(select(User).where(User.email == member_data.user_email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if already member
    existing = session.exec(
        select(GroupMembership).where(
            GroupMembership.group_id == UUID(group_id),
            GroupMembership.user_id == user.id
        )
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="User is already a member of this group")
    
    # Add membership
    membership = GroupMembership(
        group_id=UUID(group_id),
        user_id=user.id
    )
    session.add(membership)
    session.commit()
    session.refresh(membership)
    
    return {
        "membership_id": str(membership.id),
        "message": "Member added successfully"
    }

@router.delete("/groups/{group_id}/members/{user_id}")
def remove_group_member(
    group_id: str,
    user_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Remove a member from a group (org_admin only)"""
    # Get group
    group = session.get(Group, UUID(group_id))
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Check permissions
    if not check_org_admin(current_user, str(group.organization_id), session):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Find membership
    membership = session.exec(
        select(GroupMembership).where(
            GroupMembership.group_id == UUID(group_id),
            GroupMembership.user_id == UUID(user_id)
        )
    ).first()
    
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")
    
    session.delete(membership)
    session.commit()
    
    return {"message": "Member removed successfully"}

@router.delete("/groups/{group_id}/members/me")
def leave_group(
    group_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Leave a group (current user)"""
    # Check if membership exists
    membership = session.exec(
        select(GroupMembership).where(
            GroupMembership.group_id == UUID(group_id),
            GroupMembership.user_id == current_user.id
        )
    ).first()
    
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")
    
    session.delete(membership)
    session.commit()
    
    return {"message": "Left group successfully"}
