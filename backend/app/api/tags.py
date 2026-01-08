from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Optional
from pydantic import BaseModel
from app.database import get_session
from app.models import Tag, Organization, Membership, Role, EventTag, User
from app.api.auth import get_current_user
from uuid import UUID

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

@router.get("/organizations/{org_id}/tags")
def get_organization_tags(
    org_id: str,
    session: Session = Depends(get_session)
):
    """Get all tags for an organization"""
    tags = session.exec(
        select(Tag).where(Tag.organization_id == UUID(org_id))
    ).all()
    
    return [
        {
            "id": str(tag.id),
            "name": tag.name,
            "color": tag.color,
            "organization_id": str(tag.organization_id)
        }
        for tag in tags
    ]

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

@router.delete("/tags/{tag_id}")
def delete_tag(
    tag_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete a tag (org_admin only)"""
    # Get tag
    tag = session.get(Tag, UUID(tag_id))
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    # Check permissions
    if not check_org_admin(current_user, str(tag.organization_id), session):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Delete tag
    session.delete(tag)
    session.commit()
    
    return {"message": "Tag deleted successfully"}
