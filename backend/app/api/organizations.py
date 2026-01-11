from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, col
from typing import List
from app.database import get_session
from app.models import Organization, User, Membership, Role, EventVisibility
from app.api.auth import get_current_user

from app.schemas import OrganizationRead

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
    
    # Add creator as Org Admin
    membership = Membership(user_id=current_user.id, organization_id=org.id, role=Role.ORG_ADMIN) # type: ignore
    session.add(membership)
    session.commit()
    
    return org

@router.get("/", response_model=List[OrganizationRead])
def list_organizations(session: Session = Depends(get_session)):
    return session.exec(select(Organization)).all()

@router.get("/{org_id}", response_model=OrganizationRead)
def get_organization(org_id: str, session: Session = Depends(get_session)):
    org = session.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org

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
    if not membership or membership.organization_id != org_id:
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
    if not membership or membership.organization_id != org_id:
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

@router.get("/{org_id}/events")
def get_organization_events(org_id: str, session: Session = Depends(get_session)):
    """Get future events for an organization"""
    from datetime import datetime
    from app.models import Event
    
    events = session.exec(
        select(Event).where(
            Event.organization_id == org_id,
            Event.start_time >= datetime.utcnow(),
            Event.visibility != EventVisibility.DRAFT
        ).order_by(col(Event.start_time))
    ).all()
    
    return events

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
    org.color_chroma = org_update.color_chroma
    org.color_hue = org_update.color_hue
    
    from datetime import datetime
    org.updated_at = datetime.utcnow()
    
    session.add(org)
    session.commit()
    session.refresh(org)
    
    return org
