from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app.api.auth import get_current_user
from app.database import get_session
from app.models import EventTag, Membership, Organization, Role, Tag, User
from app.schemas import TagRead

router = APIRouter()

# Request models
class TagCreate(BaseModel):
    name: str
    color: str

class TagUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None

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

@router.get("/organizations/{org_id}/tags", response_model=List[TagRead])
def get_organization_tags(
    org_id: str,
    current_user: Optional[User] = Depends(get_current_user), # Use optional if public access needed, but here likely requires auth
    session: Session = Depends(get_session)
):
    """Get all tags for an organization"""
    tags = session.exec(
        select(Tag).where(Tag.organization_id == UUID(org_id))
    ).all()
    
    # Map to schema manually to handle logic or let Pydantic, but we need conditional logic
    # Actually, simpler: just return the objects.
    # We must ensure sensitive fields are filtered if not authorized.
    # Since `TagRead` includes `is_auto_approved`, we should unset it if not superadmin.
    
    return [tag.to_read_model(current_user) for tag in tags]

@router.post("/organizations/{org_id}/tags")
def create_tag(
    org_id: str,
    tag_data: TagCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Create a new tag (org_admin only)"""
    # Check permissions
    if not check_org_admin(current_user, org_id, session):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Verify organization exists
    org = session.get(Organization, UUID(org_id))
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Create tag
    tag = Tag(
        name=tag_data.name,
        color=tag_data.color,
        organization_id=UUID(org_id)
    )
    session.add(tag)
    session.commit()
    session.refresh(tag)
    
    return {
        "id": str(tag.id),
        "name": tag.name,
        "color": tag.color,
        "organization_id": str(tag.organization_id)
    }

@router.put("/tags/{tag_id}")
def update_tag(
    tag_id: str,
    tag_data: TagUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update a tag (org_admin only)"""
    # Get tag
    tag = session.get(Tag, UUID(tag_id))
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    # Check permissions
    if not check_org_admin(current_user, str(tag.organization_id), session):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Update fields
    if tag_data.name is not None:
        tag.name = tag_data.name
    if tag_data.color is not None:
        tag.color = tag_data.color
    
    session.add(tag)
    session.commit()
    session.refresh(tag)
    
    return {
        "id": str(tag.id),
        "name": tag.name,
        "color": tag.color
    }

 

@router.put("/tags/{tag_id}/auto-approve")
def toggle_auto_approve(
    tag_id: str,
    is_auto_approved: bool,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Toggle auto-approve status for a tag (Superadmin only)"""
    if not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    tag = session.get(Tag, UUID(tag_id))
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
        
    tag.is_auto_approved = is_auto_approved
    session.add(tag)
    session.commit()
    session.refresh(tag)
    
    return tag
