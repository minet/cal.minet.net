from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, ForeignKey
from sqlmodel import Field, Relationship, SQLModel, Session

GHOST_USER_ID = UUID("00000000-0000-4000-8000-000000000001")
GHOST_ORGANIZATION_ID = UUID("00000000-0000-4000-8000-000000000002")


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


class PaymentFormStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class PaymentType(str, Enum):
    HELLOASSO = "helloasso"
    CREDIT_CARD = "credit_card"
    CASH = "cash"
    CHEQUE = "cheque"
    EXCHANGE = "exchange"
    NONE = "none"
    OTHER = "other"


class ChangelogAudience(str, Enum):
    ALL = "all"
    ORG_VIEWER_PLUS = "org_viewer_plus"
    ORG_MEMBER_PLUS = "org_member_plus"
    ORG_ADMIN_PLUS = "org_admin_plus"
    TREASURY = "treasury"


class ChangelogEntry(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str
    content: str
    audience: ChangelogAudience = Field(default=ChangelogAudience.ALL)
    image_urls: Optional[str] = None  # JSON list of allowed image URLs
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)


class EventGuestOrganization(SQLModel, table=True):
    event_id: UUID = Field(foreign_key="event.id", primary_key=True)
    organization_id: UUID = Field(foreign_key="organization.id", primary_key=True)


class UserPushToken(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    endpoint: str = Field(index=True)
    keys: str  # JSON string of keys
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user: "User" = Relationship(back_populates="push_tokens")


class UserLink(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    name: str
    url: str
    order: int = Field(default=0)

    user: Optional["User"] = Relationship(back_populates="links")


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
    phone_number: Optional[str] = None
    is_active: bool = Field(default=True)
    is_superadmin: bool = Field(default=False)
    exempt_from_rgpd_delete: bool = Field(default=False)
    notification_delay: int = Field(default=45)  # Minutes before event
    profile_picture_file_id: Optional[UUID] = Field(
        default=None, foreign_key="storedfile.id"
    )
    last_seen_changelog_id: Optional[UUID] = Field(
        default=None, foreign_key="changelogentry.id"
    )

    memberships: List["Membership"] = Relationship(back_populates="user")
    subscriptions: List["Subscription"] = Relationship(back_populates="user")
    push_tokens: List["UserPushToken"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    links: List["UserLink"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    def to_public_read_model(self):
        from app.schemas import UserPublicRead

        return UserPublicRead.from_model(self)


class OrganizationImage(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    organization_id: UUID = Field(foreign_key="organization.id")
    filename: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    stored_file_id: Optional[UUID] = Field(default=None, foreign_key="storedfile.id")

    organization: Optional["Organization"] = Relationship(back_populates="images")


class Organization(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(unique=True, index=True)
    slug: str = Field(unique=True, index=True)
    description: Optional[str] = None
    color_primary: Optional[str] = Field(default=None)
    color_secondary: Optional[str] = Field(default=None)
    color_dark: Optional[str] = Field(default=None)
    type: OrganizationType
    parent_id: Optional[UUID] = Field(default=None, foreign_key="organization.id")
    delete_after: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    logo_file_id: Optional[UUID] = Field(default=None, foreign_key="storedfile.id")

    parent: Optional["Organization"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": "Organization.id"},
    )
    children: List["Organization"] = Relationship(back_populates="parent")
    members: List["Membership"] = Relationship(back_populates="organization")
    events: List["Event"] = Relationship(back_populates="organization")
    tags: List["Tag"] = Relationship(back_populates="organization")
    subscribers: List["Subscription"] = Relationship(back_populates="organization")
    groups: List["Group"] = Relationship(back_populates="organization")
    images: List["OrganizationImage"] = Relationship(
        back_populates="organization",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    organization_links: List["OrganizationLink"] = Relationship(
        back_populates="organization"
    )
    guest_events: List["Event"] = Relationship(
        back_populates="guest_organizations", link_model=EventGuestOrganization
    )

    def to_read_model(self, session=None):
        from app.schemas import OrganizationRead

        return OrganizationRead.from_model(self, session)


class Membership(SQLModel, table=True):
    """Link between User and Organization with a specific Role"""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    organization_id: UUID = Field(foreign_key="organization.id")
    role: Role = Field(default=Role.ORG_VIEWER)
    title: Optional[str] = Field(default=None)
    order: int = Field(default=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    can_manage_payment_forms: bool = Field(default=False)

    user: User = Relationship(back_populates="memberships")
    organization: Organization = Relationship(back_populates="members")


class Tag(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    color: str
    is_auto_approved: bool = Field(default=False)
    organization_id: UUID = Field(foreign_key="organization.id")

    organization: Organization = Relationship(back_populates="tags")
    event_links: List["EventTag"] = Relationship(back_populates="tag")
    subscribers: List["Subscription"] = Relationship(back_populates="tag")

    def to_read_model(self, user: Optional["User"] = None):
        from app.schemas import TagRead

        return TagRead.from_model(self, user)


class OrganizationLink(SQLModel, table=True):
    """Links attached to organizations"""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    organization_id: UUID = Field(foreign_key="organization.id")
    name: str  # Link display name
    url: str  # Link URL
    order: int = 1  # For ordering

    organization: Optional["Organization"] = Relationship(
        back_populates="organization_links"
    )


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
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

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
    group_id: Optional[UUID] = Field(default=None, foreign_key="group.id")
    poster_file_id: Optional[UUID] = Field(default=None, foreign_key="storedfile.id")
    video_file_id: Optional[UUID] = Field(default=None, foreign_key="storedfile.id")
    organization_id: UUID = Field(foreign_key="organization.id")
    created_by_id: UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    rejection_message: Optional[str] = None
    hide_details: bool = Field(default=False)
    approved_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    featured: int = Field(default=0)
    # For my bro google calendar (all my homies hate him)
    sequence: int = Field(default=0)
    updated_at: Optional[datetime] = None

    organization: Optional[Organization] = Relationship(back_populates="events")
    group: Optional["Group"] = Relationship(back_populates="events")
    event_links: List["EventLink"] = Relationship(back_populates="event")
    event_tags: List["EventTag"] = Relationship(back_populates="event")
    guest_organizations: List[Organization] = Relationship(
        back_populates="guest_events", link_model=EventGuestOrganization
    )
    reactions: List["EventReaction"] = Relationship(back_populates="event")
    payment_forms: List["EventPaymentForm"] = Relationship(back_populates="event")

    def to_read_model(
        self, current_user: Optional["User"] = None, session: Optional["Session"] = None
    ):
        from app.schemas import EventRead

        return EventRead.from_model(self, current_user, session)


class Group(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    organization_id: UUID = Field(foreign_key="organization.id")
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    organization: Optional[Organization] = Relationship(back_populates="groups")
    members: List["GroupMembership"] = Relationship(back_populates="group")
    events: List[Event] = Relationship(back_populates="group")


class GroupMembership(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    group_id: UUID = Field(foreign_key="group.id")
    user_id: UUID = Field(foreign_key="user.id")
    joined_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    group: Optional[Group] = Relationship(back_populates="members")
    user: Optional[User] = (
        Relationship()
    )  # Assuming User has a back_populates for GroupMembership


class Subscription(SQLModel, table=True):
    """User subscription to an Organization or Tag"""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    organization_id: Optional[UUID] = Field(default=None, foreign_key="organization.id")
    tag_id: Optional[UUID] = Field(default=None, foreign_key="tag.id")
    subscribe_all: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user: Optional[User] = Relationship(back_populates="subscriptions")
    organization: Optional[Organization] = Relationship(back_populates="subscribers")
    tag: Optional[Tag] = Relationship(back_populates="subscribers")


class EventReaction(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    event_id: UUID = Field(foreign_key="event.id")
    user_id: UUID = Field(foreign_key="user.id")
    emoji: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    event: Optional[Event] = Relationship(back_populates="reactions")
    user: Optional[User] = Relationship()


class LDAPUser(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    full_name: Optional[str] = None
    uid: Optional[str] = Field(default=None, index=True)
    synced_at: datetime = Field(default_factory=datetime.now)


class ShortLinkType(str, Enum):
    EVENT = "EVENT"
    ORGANIZATION = "ORGANIZATION"
    TAG = "TAG"


class ShortLinkActionType(str, Enum):
    VIEW = "VIEW"
    SUBSCRIBE = "SUBSCRIBE"
    COUNTDOWN = "COUNTDOWN"
    PAYMENT = "PAYMENT"


class ShortLink(SQLModel, table=True):
    id: str = Field(primary_key=True)
    item_type: ShortLinkType
    action_type: ShortLinkActionType
    item_id: UUID
    created_by_id: UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_used_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user: Optional[User] = Relationship()


class OrganizationHelloAsso(SQLModel, table=True):
    """Stores per-organization HelloAsso API credentials (encrypted at rest).

    The api_client_secret is Fernet-encrypted and is NEVER returned by the API.
    Cached access tokens (also encrypted) avoid hitting HelloAsso on every request.
    """

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    organization_id: UUID = Field(foreign_key="organization.id", unique=True)
    helloasso_slug: str  # The org's slug on HelloAsso
    api_client_id: str  # HelloAsso client_id (can be shown to admins)
    api_client_secret: str  # Fernet-encrypted client_secret — never returned via API
    # Cached OAuth2 token from client_credentials grant:
    cached_access_token: Optional[str] = None  # Fernet-encrypted
    token_expires_at: Optional[datetime] = None
    connected_by_id: UUID = Field(foreign_key="user.id")
    connected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EventPaymentFormOptionUser(SQLModel, table=True):
    """Join table: which users may select a specific private option."""

    option_id: UUID = Field(foreign_key="eventpaymentformoption.id", primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", primary_key=True)

    option: Optional["EventPaymentFormOption"] = Relationship(
        back_populates="allowed_user_links"
    )
    user: Optional["User"] = Relationship()


class EventPaymentFormOption(SQLModel, table=True):
    """A selectable add-on option for a payment form (replaces the JSON options column)."""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    payment_form_id: UUID = Field(foreign_key="eventpaymentform.id", index=True)
    name: str
    price_cents: int
    is_private: bool = Field(default=False)
    order: int = Field(default=0)

    payment_form: Optional["EventPaymentForm"] = Relationship(
        back_populates="form_options"
    )
    allowed_user_links: List["EventPaymentFormOptionUser"] = Relationship(
        back_populates="option",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class EventPaymentForm(SQLModel, table=True):
    """A payment form proposal attached to an event.

    Created by a member with can_manage_payment_forms; must be approved by
    the parent org admin before HelloAsso is called and the URL is published.
    """

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    event_id: UUID = Field(foreign_key="event.id", unique=True)
    requesting_org_id: UUID = Field(foreign_key="organization.id")  # Child org
    approving_org_id: Optional[UUID] = Field(
        default=None, foreign_key="organization.id"
    )  # Parent org
    total_amount_cents: int
    item_name: str
    status: PaymentFormStatus = Field(default=PaymentFormStatus.PENDING)
    # Whether new payments can be initiated (admins can close/reopen)
    is_open: bool = Field(default=True)
    # No HelloAsso URL stored here — checkout intents are created on demand
    # when each user initiates payment. last_checkout_intent_id is kept for
    # webhook matching only (the most recently generated intent).
    last_checkout_intent_id: Optional[str] = None
    rejection_message: Optional[str] = None
    payment_completed: bool = Field(
        default=False
    )  # Set to True on first completed payment
    # Baseline counters for entries removed upon user account deletion (RGPD)
    baseline_total_amount_cents: int = Field(default=0)
    baseline_participant_count: int = Field(default=0)
    created_by_id: UUID = Field(foreign_key="user.id")
    reviewed_by_id: Optional[UUID] = Field(default=None, foreign_key="user.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    reviewed_at: Optional[datetime] = None

    event: Event = Relationship(back_populates="payment_forms")
    requesting_org: "Organization" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[EventPaymentForm.requesting_org_id]"}
    )
    approving_org: Optional["Organization"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[EventPaymentForm.approving_org_id]"}
    )
    created_by: "User" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[EventPaymentForm.created_by_id]"}
    )
    reviewed_by: Optional["User"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[EventPaymentForm.reviewed_by_id]"}
    )
    form_options: List["EventPaymentFormOption"] = Relationship(
        back_populates="payment_form",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    entries: List["EventPaymentEntry"] = Relationship(back_populates="payment_form")
    billeterie: Optional["PaymentFormBilleterie"] = Relationship(
        back_populates="payment_form",
        sa_relationship_kwargs={"uselist": False, "cascade": "all, delete-orphan"},
    )


class EventPaymentEntry(SQLModel, table=True):
    """Tracks individual per-user payment initiations and completions.

    Created when a user clicks 'Pay' (helloasso type) or added manually by org admins.
    For manual entries, user_id and checkout_intent_id may be None.
    """

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    payment_form_id: UUID = Field(foreign_key="eventpaymentform.id", index=True)
    user_id: Optional[UUID] = Field(default=None, foreign_key="user.id")
    checkout_intent_id: Optional[str] = Field(default=None, index=True, unique=True)
    helloasso_payment_id: Optional[str] = Field(default=None, index=True, unique=True)
    helloasso_order_id: Optional[str] = Field(default=None, index=True, unique=True)
    completed: bool = Field(default=False)
    completed_at: Optional[datetime] = None
    # JSON list of EventPaymentFormOption UUIDs chosen by the payer
    selected_option_ids: Optional[str] = None
    amount_cents: int  # base + selected options
    payment_type: str = Field(default="helloasso")  # PaymentType enum value
    # For manual entries: name of the attendee (not a registered user)
    attendee_name: Optional[str] = None
    # For billeterie imports: JSON list of {"name": str, "amount_cents": int}
    imported_options: Optional[str] = None
    # Ticket validation (checked at entrance)
    validated: bool = Field(default=False)
    validated_at: Optional[datetime] = None
    validated_by_id: Optional[UUID] = Field(default=None, foreign_key="user.id")
    # Cancellation (entry hidden from validation view)
    cancelled: bool = Field(default=False)
    cancelled_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    payment_form: EventPaymentForm = Relationship(back_populates="entries")
    user: Optional["User"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[EventPaymentEntry.user_id]"}
    )
    validated_by: Optional["User"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[EventPaymentEntry.validated_by_id]"}
    )


class PaymentFormBilleterie(SQLModel, table=True):
    """Links a payment form to a HelloAsso billeterie (ticketing event) for attendee import.

    Only users with can_manage_payment_forms on the org that *directly* has HelloAsso
    configured can create or remove this link.  The link is restricted to the same
    org hierarchy: the HA org must be an ancestor-or-equal of the form's requesting org.
    """

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    payment_form_id: UUID = Field(foreign_key="eventpaymentform.id", unique=True)
    # FK to OrganizationHelloAsso.id (not organization.id) so cascade-delete works
    # when the HA integration is removed.
    helloasso_org_id: UUID = Field(
        sa_column=Column(
            ForeignKey("organizationhelloasso.id", ondelete="CASCADE"), nullable=False
        )
    )
    helloasso_form_slug: str
    helloasso_form_title: str
    helloasso_form_type: str = Field(default="Event")
    last_imported_at: Optional[datetime] = None
    created_by_id: UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    payment_form: "EventPaymentForm" = Relationship(back_populates="billeterie")
    helloasso_org: Optional["OrganizationHelloAsso"] = Relationship()
    created_by: Optional["User"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[PaymentFormBilleterie.created_by_id]"}
    )


class StoredFile(SQLModel, table=True):
    """Tracks every file uploaded to MinIO storage"""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    stored_filename: str = Field(index=True)  # unique name in MinIO (e.g. "abc123.mp4")
    original_filename: str  # original name from the user's machine
    url: str  # public URL (/uploads/abc123.mp4)
    content_type: str
    size: int  # bytes
    uploaded_by_id: UUID = Field(foreign_key="user.id")
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    processed: bool = Field(default=False)
    file_type: str = Field(default="image")  # "image" or "video"
    variants: Optional[str] = Field(default=None)  # JSON list of variant dicts
    retry_count: int = Field(default=0)
