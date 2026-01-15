from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session, select, or_
from starlette.config import Config
from typing import List, Optional
from app.database import get_session
from app.models import User, Organization, Membership, Role, Group, GroupMembership
from app.api.auth import get_current_user
from pydantic import BaseModel
from app.utils.email import send_email

router = APIRouter()
config = Config('.env')

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    profile_picture_url: Optional[str] = None
    phone_number: Optional[str] = None
    facebook_link: Optional[str] = None

class UserInvite(BaseModel):
    email: str

class UserSearchResult(BaseModel):
    id: str
    full_name: Optional[str] = None
    profile_picture_url: Optional[str] = None

    class Config:
        from_attributes = True

class MembershipWithOrganization(BaseModel):
    id: str
    user_id: str
    organization_id: str
    role: str
    organization: Organization | None = None

    class Config:
        from_attributes = True

@router.get("/me/organizations", response_model=List[Organization])
async def get_user_organizations(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get all organizations where the current user is a member (any role)"""
    memberships = session.exec(
        select(Membership).where(Membership.user_id == current_user.id)
    ).all()
    
    org_ids = [m.organization_id for m in memberships]
    if not org_ids:
        return []
    
    organizations = session.exec(
        select(Organization).where(Organization.id.in_(org_ids)) #pyright: ignore
    ).all()
    
    return organizations

@router.get("/me/memberships", response_model=List[MembershipWithOrganization])
async def get_user_memberships(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get all memberships for the current user with organization details"""
    memberships = session.exec(
        select(Membership).where(Membership.user_id == current_user.id)
    ).all()
    
    result = []
    for membership in memberships:
        org = session.get(Organization, membership.organization_id)
        result.append(MembershipWithOrganization(
            id=str(membership.id),
            user_id=str(membership.user_id),
            organization_id=str(membership.organization_id),
            role=membership.role.value,
            organization=org
        ))
    
    return result

@router.get("/me/groups")
async def get_user_groups(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get all groups for the current user"""
    memberships = session.exec(
        select(GroupMembership).where(GroupMembership.user_id == current_user.id)
    ).all()
    
    result = []
    for membership in memberships:
        group = session.get(Group, membership.group_id)
        if group:
            # We also want organization info for display
            organization = session.get(Organization, group.organization_id)
            if organization:
                result.append({
                    "id": str(group.id),
                    "name": group.name,
                    "description": group.description,
                    "organization": {
                        "id": str(organization.id),
                        "name": organization.name,
                        "logo_url": organization.logo_url
                    },
                    "membership_id": str(membership.id),
                    "joined_at": membership.joined_at.isoformat()
                })
    
    return result

@router.get("/{user_id}/memberships", response_model=List[MembershipWithOrganization])
async def get_other_user_memberships(
    user_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get memberships for a specific user"""
    # Allow if superadmin or if requesting own memberships
    if not current_user.is_superadmin and str(current_user.id) != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    memberships = session.exec(
        select(Membership).where(Membership.user_id == UUID(user_id))
    ).all()
    
    result = []
    for membership in memberships:
        org = session.get(Organization, membership.organization_id)
        result.append(MembershipWithOrganization(
            id=str(membership.id),
            user_id=str(membership.user_id),
            organization_id=str(membership.organization_id),
            role=membership.role.value,
            organization=org
        ))
    
    return result

from app.schemas import UserRead, UserPublicRead

# ... imports ...

@router.put("/me", response_model=UserRead)
async def update_user_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update current user's profile"""
    user = session.get(User, current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update fields if provided
    if user_data.full_name is not None:
        user.full_name = user_data.full_name
    if user_data.profile_picture_url is not None:
        user.profile_picture_url = user_data.profile_picture_url
    if user_data.phone_number is not None:
        user.phone_number = user_data.phone_number
    if user_data.facebook_link is not None:
        user.facebook_link = user_data.facebook_link
    
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return user

@router.get("/search", response_model=List[UserSearchResult])
async def search_users(
    q: str = Query(..., min_length=1, description="Search query"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Search users by name or email"""
    search_pattern = f"%{q}%"
    
    users = session.exec(
        select(User).where(
            or_(
                User.full_name.ilike(search_pattern), #pyright: ignore
                User.email.ilike(search_pattern) #pyright: ignore
            )
        ).limit(20)
    ).all()
    
    return [
        UserSearchResult(
            id=str(user.id),
            full_name=user.full_name,
            profile_picture_url=user.profile_picture_url
        )
        for user in users
    ]

from uuid import UUID

@router.get("/{user_id}", response_model=UserRead)
async def get_user_profile(
    user_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get a user's public profile by ID"""
    if user_id == "me":
        # Ensure we return UserRead compatible dict
        return current_user

    user = session.get(User, UUID(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

@router.get("/", response_model=List[UserRead])
async def list_users(
    skip: int = 0, 
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """List all users (Superadmin only)"""
    if not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    users = session.exec(select(User).offset(skip).limit(limit)).all()
    return users

@router.post("/invite", response_model=UserRead)
async def invite_user(
    invite: UserInvite,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Invite a new user (Superadmin only)"""
    if not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Only superadmins can invite users")
    
    existing = session.exec(select(User).where(User.email == invite.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    
    user = User(
        email=invite.email,
        full_name=None, # Will be filled on first OIDC login
        is_active=True,
        is_superadmin=False
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # Send email
    app_url = config.get("APP_BASE_URL")
    
    html_content = f"""
    <h1>Welcome to Calend'INT!</h1>
    <p>You have been invited to join.</p>
    <p>Please login to set up your account: <a href="{app_url}/login">{app_url}/login</a></p>
    """
    try:
        send_email(user.email, "Welcome to Calend'INT", html_content)
    except Exception as e:
        print(f"Error sending email: {e}")
    
    return user

@router.put("/{user_id}/superadmin", response_model=UserRead)
async def toggle_superadmin(
    user_id: str,
    is_superadmin: bool,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Toggle superadmin status"""
    if not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    user = session.get(User, UUID(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_superadmin = is_superadmin
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return user

@router.put("/{user_id}/active", response_model=UserRead)
async def toggle_active(
    user_id: str,
    is_active: bool,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Toggle user active status (Ban/Unban)"""
    if not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    user = session.get(User, UUID(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent banning yourself
    if user.id == current_user.id and not is_active:
        raise HTTPException(status_code=400, detail="Cannot ban yourself")

    user.is_active = is_active
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return user

@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete a user"""
    if not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    user = session.get(User, UUID(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Prevent deleting yourself
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    session.delete(user)
    session.commit()
    
    return {"ok": True}
