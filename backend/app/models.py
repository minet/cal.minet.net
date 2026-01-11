from typing import Optional, List
from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum

class OrganizationType(str, Enum):
    ASSOCIATION = "association"
    CLUB = "club"
    LISTE = "liste"
    ADMINISTRATION = "administration"
    GATE = "gate"

class Role(str, Enum):
    ORG_ADMIN = "org_admin"
    ORG_MEMBER = "org_member"
    ORG_VIEWER = "org_viewer"

class EventGuestOrganization(SQLModel, table=True):
    event_id: UUID = Field(foreign_key="event.id", primary_key=True)
    organization_id: UUID = Field(foreign_key="organization.id", primary_key=True)

class EventVisibility(str, Enum):
    DRAFT = "draft"
    PRIVATE = "private"
    PUBLIC_PENDING = "public_pending"
    PUBLIC_REJECTED = "public_rejected"
    PUBLIC_APPROVED = "public_approved"

class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    full_name: Optional[str] = None
    profile_picture_url: Optional[str] = None
    facebook_link: Optional[str] = None
    phone_number: Optional[str] = None
    is_active: bool = Field(default=True)
    is_superadmin: bool = Field(default=False)

    memberships: List["Membership"] = Relationship(back_populates="user")
    subscriptions: List["Subscription"] = Relationship(back_populates="user")

class Organization(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(unique=True, index=True)
    slug: str = Field(unique=True, index=True)
    description: Optional[str] = None
    logo_url: Optional[str] = None
    color_chroma: Optional[float] = Field(default=None)
    color_hue: Optional[float] = Field(default=None)
    type: OrganizationType
    parent_id: Optional[UUID] = Field(default=None, foreign_key="organization.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    parent: Optional["Organization"] = Relationship(back_populates="children", sa_relationship_kwargs={"remote_side": "Organization.id"})
    children: List["Organization"] = Relationship(back_populates="parent")
    members: List["Membership"] = Relationship(back_populates="organization")
    events: List["Event"] = Relationship(back_populates="organization")
    tags: List["Tag"] = Relationship(back_populates="organization")
    subscribers: List["Subscription"] = Relationship(back_populates="organization")
    groups: List["Group"] = Relationship(back_populates="organization")
    organization_links: List["OrganizationLink"] = Relationship(back_populates="organization")
    guest_events: List["Event"] = Relationship(back_populates="guest_organizations", link_model=EventGuestOrganization)

class Membership(SQLModel, table=True):
    """Link between User and Organization with a specific Role"""
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    organization_id: UUID = Field(foreign_key="organization.id")
    role: Role = Field(default=Role.ORG_VIEWER)

    user: User = Relationship(back_populates="memberships")
    organization: Organization = Relationship(back_populates="members")

class Tag(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    color: str
    organization_id: UUID = Field(foreign_key="organization.id")

    organization: Organization = Relationship(back_populates="tags")
    event_links: List["EventTag"] = Relationship(back_populates="tag")
    subscribers: List["Subscription"] = Relationship(back_populates="tag")


class OrganizationLink(SQLModel, table=True):
    """Links attached to organizations"""
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    organization_id: UUID = Field(foreign_key="organization.id")
    name: str  # Link display name
    url: str  # Link URL
    order: int = 1  # For ordering
    
    organization: Optional["Organization"] = Relationship(back_populates="organization_links")

class EventLink(SQLModel, table=True):
    """Links attached to events (up to 3 per event)"""
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    event_id: UUID = Field(foreign_key="event.id")
    name: str  # Link display name
    url: str  # Link URL
    order: int = 1  # 1-3 for ordering

    event: Optional["Event"] = Relationship(back_populates="event_links")

class EventTag(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    event_id: UUID = Field(foreign_key="event.id")
    tag_id: UUID = Field(foreign_key="tag.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    event: Optional["Event"] = Relationship(back_populates="event_tags")
    tag: Tag = Relationship(back_populates="event_links")

class Event(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    location_url: Optional[str] = None
    visibility: EventVisibility = Field(default=EventVisibility.PUBLIC_PENDING)
    show_on_schedule: bool = Field(default=False)
    group_id: Optional[UUID] = Field(default=None, foreign_key="group.id")
    poster_url: Optional[str] = None
    organization_id: UUID = Field(foreign_key="organization.id")
    created_by_id: UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    # New fields for approval workflow
    rejection_message: Optional[str] = None
    hide_details: bool = Field(default=False)
    approved_at: Optional[datetime] = None

    organization: Optional[Organization] = Relationship(back_populates="events")
    group: Optional["Group"] = Relationship(back_populates="events")
    event_links: List["EventLink"] = Relationship(back_populates="event")
    event_tags: List["EventTag"] = Relationship(back_populates="event")
    guest_organizations: List[Organization] = Relationship(back_populates="guest_events", link_model=EventGuestOrganization)
    reactions: List["EventReaction"] = Relationship(back_populates="event")

class Group(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    organization_id: UUID = Field(foreign_key="organization.id")
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    organization: Optional[Organization] = Relationship(back_populates="groups")
    members: List["GroupMembership"] = Relationship(back_populates="group")
    events: List[Event] = Relationship(back_populates="group")

class GroupMembership(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    group_id: UUID = Field(foreign_key="group.id")
    user_id: UUID = Field(foreign_key="user.id")
    joined_at: datetime = Field(default_factory=datetime.utcnow)

    group: Optional[Group] = Relationship(back_populates="members")
    user: Optional[User] = Relationship() # Assuming User has a back_populates for GroupMembership

class Subscription(SQLModel, table=True):
    """User subscription to an Organization or Tag"""
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    organization_id: Optional[UUID] = Field(default=None, foreign_key="organization.id")
    tag_id: Optional[UUID] = Field(default=None, foreign_key="tag.id")
    subscribe_all: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional[User] = Relationship(back_populates="subscriptions")
    organization: Optional[Organization] = Relationship(back_populates="subscribers")
    tag: Optional[Tag] = Relationship(back_populates="subscribers")



class EventReaction(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    event_id: UUID = Field(foreign_key="event.id")
    user_id: UUID = Field(foreign_key="user.id")
    emoji: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    event: Optional[Event] = Relationship(back_populates="reactions")
    user: Optional[User] = Relationship()
