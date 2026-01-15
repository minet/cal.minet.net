from pydantic import BaseModel
from typing import List, Optional, Any, TYPE_CHECKING
from datetime import datetime
from uuid import UUID
from app.models import OrganizationType, EventVisibility, Role

if TYPE_CHECKING:
    from app.models import Tag, Organization, User, Event, Membership
    from sqlmodel import Session

class TagRead(BaseModel):
    id: UUID
    name: str
    color: str
    organization_id: UUID
    is_auto_approved: Optional[bool] = None

    @classmethod
    def from_model(cls, tag: "Tag", user: Optional["User"] = None) -> "TagRead":
        is_super = user.is_superadmin if user else False
        return cls(
            id=tag.id,
            name=tag.name,
            color=tag.color,
            organization_id=tag.organization_id,
            is_auto_approved=tag.is_auto_approved if is_super else None
        )

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

    @classmethod
    def from_model(cls, org: "Organization") -> "OrganizationRead":
        links = [OrganizationLinkRead(id=l.id, name=l.name, url=l.url, order=l.order) for l in org.organization_links]
        return cls(
            id=org.id,
            name=org.name,
            logo_url=org.logo_url,
            type=org.type,
            slug=org.slug,
            description=org.description,
            parent_id=org.parent_id,
            color_chroma=org.color_chroma,
            color_hue=org.color_hue,
            created_at=org.created_at,
            updated_at=org.updated_at,
            organization_links=links
        )

class UserRead(BaseModel):
    id: UUID
    email: str
    full_name: Optional[str] = None
    profile_picture_url: Optional[str] = None
    phone_number: Optional[str] = None
    facebook_link: Optional[str] = None
    is_superadmin: bool = False
    is_active: bool = True

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

    @classmethod
    def from_model(cls, user: "User") -> "UserPublicRead":
        return cls(
            id=user.id,
            full_name=user.full_name,
            profile_picture_url=user.profile_picture_url,
            phone_number=user.phone_number,
            facebook_link=user.facebook_link
        )

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
    poster_url: Optional[str] = None

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

    @classmethod
    def from_model(cls, event: "Event", current_user: Optional["User"] = None, session: Optional["Session"] = None) -> "EventRead":
        from app.models import Role, Membership, User
        from sqlmodel import select

        # Logic to determine if user can see details
        should_hide = False
        if event.hide_details and event.visibility == EventVisibility.PUBLIC_APPROVED:
             is_auth = False
             if current_user:
                 if current_user.is_superadmin:
                     is_auth = True
                 elif session:
                     # Check membership
                     membership = session.exec(
                        select(Membership).where(
                            Membership.user_id == current_user.id,
                            Membership.organization_id == event.organization_id
                        )
                     ).first()
                     if membership:
                         is_auth = True
             
             if not is_auth:
                 should_hide = True

        # Tags
        tags_read = [
            TagRead.from_model(et.tag, current_user) 
            for et in event.event_tags 
            if et.tag
        ]
        
        # Guest Orgs
        guest_orgs_read = [
            OrganizationRead.from_model(org) 
            for org in event.guest_organizations
        ]
        
        # Reactions
        reaction_counts = {}
        user_reacted_emojis = set()
        if current_user:
            for r in event.reactions:
                reaction_counts[r.emoji] = reaction_counts.get(r.emoji, 0) + 1
                if r.user_id == current_user.id:
                    user_reacted_emojis.add(r.emoji)
        else:
            for r in event.reactions:
                reaction_counts[r.emoji] = reaction_counts.get(r.emoji, 0) + 1

        reactions_summary = [
            ReactionSummary(
                emoji=emoji,
                count=count,
                user_reacted=(emoji in user_reacted_emojis)
            )
            for emoji, count in reaction_counts.items()
        ]

        creator = None
        if session and event.created_by_id:
             creator_obj = session.get(User, event.created_by_id)
             if creator_obj:
                 creator = UserPublicRead.from_model(creator_obj)

        group_read = None
        if event.group:
             group_read = GroupRead(id=event.group.id, name=event.group.name)

        from datetime import timezone

        # Ensure timezone context is preserved/added
        start_time = event.start_time.replace(tzinfo=timezone.utc) if event.start_time.tzinfo is None else event.start_time
        end_time = event.end_time.replace(tzinfo=timezone.utc) if event.end_time.tzinfo is None else event.end_time

        return cls(
            id=event.id,
            title=event.title,
            description=None if should_hide else event.description,
            start_time=start_time,
            end_time=end_time,
            location=None if should_hide else event.location,
            location_url=None if should_hide else event.location_url,
            visibility=event.visibility,
            show_on_schedule=event.show_on_schedule,
            hide_details=event.hide_details,
            poster_url=None if should_hide else event.poster_url,
            created_at=event.created_at,
            approved_at=event.approved_at,
            rejection_message=event.rejection_message if (
                current_user and (
                    current_user.id == event.created_by_id or current_user.is_superadmin
                )
            ) else None,
            
            organization=OrganizationRead.from_model(event.organization) if event.organization else None,
            guest_organizations=guest_orgs_read,
            tags=tags_read,
            group=group_read,
            
            created_by=creator,
            created_by_id=event.created_by_id,
            
            reactions=reactions_summary,
            is_draft=(event.visibility == EventVisibility.DRAFT)
        )

class Message(BaseModel):
    message: str
