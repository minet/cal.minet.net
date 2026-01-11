from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime
from uuid import UUID
from app.models import OrganizationType, EventVisibility, Role

class TagRead(BaseModel):
    id: UUID
    name: str
    color: str

class OrganizationLinkRead(BaseModel):
    id: UUID
    name: str
    url: str
    order: int

class OrganizationRead(BaseModel):
    id: UUID
    name: str
    logo_url: Optional[str] = None
    type: Optional[OrganizationType] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[UUID] = None
    color_chroma: Optional[float] = None
    color_hue: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    organization_links: List[OrganizationLinkRead] = []

class UserRead(BaseModel):
    id: UUID
    email: str
    full_name: Optional[str] = None
    profile_picture_url: Optional[str] = None
    phone_number: Optional[str] = None
    facebook_link: Optional[str] = None
    is_superadmin: bool = False

    class Config:
        from_attributes = True

class UserPublicRead(BaseModel):
    id: UUID
    full_name: Optional[str] = None
    profile_picture_url: Optional[str] = None
    phone_number: Optional[str] = None
    facebook_link: Optional[str] = None

    class Config:
        from_attributes = True

class GroupRead(BaseModel):
    id: UUID
    name: str

class CreateEvent(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    location_url: Optional[str] = None
    organization_id: str
    visibility: str = "public_pending"
    group_id: Optional[str] = None
    tag_ids: List[str] = []
    guest_organization_ids: List[str] = []
    show_on_schedule: bool = False
    hide_details: bool = False

class UpdateEvent(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    location_url: Optional[str] = None
    visibility: Optional[str] = None
    group_id: Optional[str] = None
    tag_ids: Optional[List[str]] = None
    guest_organization_ids: Optional[List[str]] = None
    show_on_schedule: Optional[bool] = None
    poster_url: Optional[str] = None
    hide_details: Optional[bool] = None

class RejectEventRequest(BaseModel):
    message: str

class ReactionSummary(BaseModel):
    emoji: str
    count: int
    user_reacted: bool

class ReactionDetail(BaseModel):
    user: UserPublicRead
    emoji: str
    created_at: datetime

class EventRead(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    location_url: Optional[str] = None
    visibility: EventVisibility
    hide_details: bool = False
    show_on_schedule: bool = False
    poster_url: Optional[str] = None
    rejection_message: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    
    organization: Optional[OrganizationRead] = None
    guest_organizations: List[OrganizationRead] = []
    tags: List[TagRead] = []
    group: Optional[GroupRead] = None
    created_by: Optional[UserPublicRead] = None
    created_by_id: Optional[UUID] = None
    
    reactions: List[ReactionSummary] = []
    
    is_draft: Optional[bool] = None

class Message(BaseModel):
    message: str
