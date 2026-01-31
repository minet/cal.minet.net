from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app.api.auth import get_current_user
from app.database import get_session
from app.models import Membership, Organization, OrganizationLink, Role, User

router = APIRouter()

class OrganizationLinkCreate(BaseModel):
    name: str
    url: str
    order: int = 1

class OrganizationLinkUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    order: Optional[int] = None

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

@router.get("/organizations/{org_id}/links")
def get_organization_links(
    org_id: str,
    session: Session = Depends(get_session)
):
    """Get all links for an organization"""
    links = session.exec(
        select(OrganizationLink)
        .where(OrganizationLink.organization_id == UUID(org_id))
        .order_by(OrganizationLink.order) # pyright: ignore
    ).all()
    
    return [
        {
            "id": str(link.id),
            "name": link.name,
            "url": link.url,
            "order": link.order
        }
        for link in links
    ]

@router.post("/organizations/{org_id}/links")
def create_organization_link(
    org_id: str,
    link_data: OrganizationLinkCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Create a new organization link (org_admin only)"""
    # Check permissions
    if not check_org_admin(current_user, org_id, session):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Verify organization exists
    org = session.get(Organization, UUID(org_id))
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Create link
    link = OrganizationLink(
        name=link_data.name,
        url=link_data.url,
        order=link_data.order,
        organization_id=UUID(org_id)
    )
    session.add(link)
    session.commit()
    session.refresh(link)
    
    return {
        "id": str(link.id),
        "name": link.name,
        "url": link.url,
        "order": link.order
    }

@router.put("/organization-links/{link_id}")
def update_organization_link(
    link_id: str,
    link_data: OrganizationLinkUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update an organization link (org_admin only)"""
    # Get link
    link = session.get(OrganizationLink, UUID(link_id))
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    # Check permissions
    if not check_org_admin(current_user, str(link.organization_id), session):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Update fields
    if link_data.name is not None:
        link.name = link_data.name
    if link_data.url is not None:
        link.url = link_data.url
    if link_data.order is not None:
        link.order = link_data.order
    
    session.add(link)
    session.commit()
    session.refresh(link)
    
    return {
        "id": str(link.id),
        "name": link.name,
        "url": link.url,
        "order": link.order
    }

@router.delete("/organization-links/{link_id}")
def delete_organization_link(
    link_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete an organization link (org_admin only)"""
    # Get link
    link = session.get(OrganizationLink, UUID(link_id))
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    # Check permissions
    if not check_org_admin(current_user, str(link.organization_id), session):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Delete link
    session.delete(link)
    session.commit()
    
    return {"message": "Link deleted successfully"}
