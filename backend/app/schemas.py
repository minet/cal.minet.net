from datetime import datetime, timedelta, timezone
from typing import Any, List, Optional, TYPE_CHECKING
from typing import Any, Generic, List, Optional, TYPE_CHECKING, TypeVar
from uuid import UUID

from pydantic import BaseModel

from app.models import (
    ChangelogAudience,
    EventVisibility,
    OrganizationType,
    PaymentFormStatus,
    PaymentType,
    Role,
)

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int
    pages: int


if TYPE_CHECKING:
    from app.models import (
        Tag,
        Organization,
        OrganizationImage,
        User,
        Event,
        Membership,
        StoredFile,
    )
    from sqlmodel import Session


class StoredFileVariantRead(BaseModel):
    width: int
    url: str
    format: str  # "webp" or "webm"
    size: int  # bytes


class StoredFileRead(BaseModel):
    id: UUID
    url: str
    variants: List[StoredFileVariantRead] = []
    processed: bool = False
    file_type: str = "image"

    @classmethod
    def from_model(cls, sf: "StoredFile") -> "StoredFileRead":
        import json as _json

        variants: List[StoredFileVariantRead] = []
        if sf.variants:
            try:
                for v in _json.loads(sf.variants):
                    variants.append(StoredFileVariantRead(**v))
            except Exception:
                pass
        return cls(
            id=sf.id,
            url=sf.url,
            variants=variants,
            processed=sf.processed,
            file_type=sf.file_type,
        )


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
            is_auto_approved=tag.is_auto_approved if is_super else None,
        )


class OrganizationLinkRead(BaseModel):
    id: UUID
    name: str
    url: str
    order: int


class OrganizationImageRead(BaseModel):
    id: UUID
    url: Optional[str] = None
    filename: str
    created_at: datetime
    stored_file: Optional[StoredFileRead] = None

    @classmethod
    def from_model(
        cls, img: "OrganizationImage", session: Optional["Session"] = None
    ) -> "OrganizationImageRead":
        stored_file = None
        if session and img.stored_file_id:
            from app.models import StoredFile

            sf = session.get(StoredFile, img.stored_file_id)
            if sf:
                stored_file = StoredFileRead.from_model(sf)
        return cls(
            id=img.id,
            url=stored_file.url if stored_file else None,
            filename=img.filename,
            created_at=img.created_at,
            stored_file=stored_file,
        )


class UserLinkRead(BaseModel):
    id: UUID
    name: str
    url: str
    order: int


class UserLinkCreate(BaseModel):
    name: str
    url: str
    order: int = 0


class EventLinkCreate(BaseModel):
    name: str
    url: str


class EventLinkRead(BaseModel):
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
    delete_after: Optional[datetime] = None
    color_primary: Optional[str] = None
    color_secondary: Optional[str] = None
    color_dark: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    organization_links: List[OrganizationLinkRead] = []
    logo_file: Optional[StoredFileRead] = None
    can_edit: Optional[bool] = None
    can_manage_payment_forms: Optional[bool] = None

    @classmethod
    def from_model(
        cls,
        org: "Organization",
        session: Optional["Session"] = None,
        membership: Optional["Membership"] = None,
    ) -> "OrganizationRead":
        links = [
            OrganizationLinkRead(id=l.id, name=l.name, url=l.url, order=l.order)
            for l in org.organization_links
        ]
        logo_file = None
        can_edit = membership.role in [Role.ORG_ADMIN] if membership else None
        can_manage_payment_forms = (
            membership.can_manage_payment_forms if membership else None
        )
        if session and org.logo_file_id:
            from app.models import StoredFile

            sf = session.get(StoredFile, org.logo_file_id)
            if sf:
                logo_file = StoredFileRead.from_model(sf)
        return cls(
            id=org.id,
            name=org.name,
            logo_url=logo_file.url if logo_file else None,
            type=org.type,
            slug=org.slug,
            description=org.description,
            parent_id=org.parent_id,
            delete_after=org.delete_after,
            color_primary=org.color_primary,
            color_secondary=org.color_secondary,
            color_dark=org.color_dark,
            created_at=org.created_at,
            updated_at=org.updated_at,
            organization_links=links,
            logo_file=logo_file,
            can_edit=can_edit,
            can_manage_payment_forms=can_manage_payment_forms,
        )


class UserRead(BaseModel):
    id: UUID
    email: str
    full_name: Optional[str] = None
    profile_picture_url: Optional[str] = None
    phone_number: Optional[str] = None
    is_superadmin: bool = False
    exempt_from_rgpd_delete: bool = False
    is_active: bool = True
    notification_delay: int = 15
    last_seen_changelog_id: Optional[UUID] = None
    links: List["UserLinkRead"] = []
    profile_picture_file: Optional[StoredFileRead] = None

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    profile_picture_file_id: Optional[str] = None  # UUID string
    phone_number: Optional[str] = None
    notification_delay: Optional[int] = None


class PushTokenCreate(BaseModel):
    endpoint: str
    keys: str


class UserPublicRead(BaseModel):
    id: UUID
    full_name: Optional[str] = None
    profile_picture_url: Optional[str] = None
    phone_number: Optional[str] = None
    links: List["UserLinkRead"] = []
    profile_picture_file: Optional[StoredFileRead] = None

    class Config:
        from_attributes = True

    @classmethod
    def from_model(
        cls, user: "User", session: Optional["Session"] = None
    ) -> "UserPublicRead":
        from app.models import UserLink

        profile_picture_file = None
        if session and user.profile_picture_file_id:
            from app.models import StoredFile

            sf = session.get(StoredFile, user.profile_picture_file_id)
            if sf:
                profile_picture_file = StoredFileRead.from_model(sf)
        return cls(
            id=user.id,
            full_name=user.full_name,
            profile_picture_url=(
                profile_picture_file.url if profile_picture_file else None
            ),
            phone_number=user.phone_number,
            links=[
                UserLinkRead(id=l.id, name=l.name, url=l.url, order=l.order)
                for l in user.links
            ],
            profile_picture_file=profile_picture_file,
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
    hide_details: bool = False
    poster_file_id: Optional[UUID] = None
    video_file_id: Optional[UUID] = None
    links: List[EventLinkCreate] = []


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
    poster_file_id: Optional[UUID] = None
    video_file_id: Optional[UUID] = None
    hide_details: Optional[bool] = None
    featured: Optional[int] = None
    links: Optional[List[EventLinkCreate]] = None


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
    poster_url: Optional[str] = None
    video_url: Optional[str] = None
    rejection_message: Optional[str] = None
    approved_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    created_at: datetime

    # New Fields
    featured: int = 0
    is_featured: bool = False

    organization: Optional[OrganizationRead] = None
    guest_organizations: List[OrganizationRead] = []
    tags: List[TagRead] = []
    event_links: List[EventLinkRead] = []
    group: Optional[GroupRead] = None
    created_by: Optional[UserPublicRead] = None
    created_by_id: Optional[UUID] = None

    reactions: List[ReactionSummary] = []

    is_draft: Optional[bool] = None

    poster_file: Optional[StoredFileRead] = None
    video_file: Optional[StoredFileRead] = None

    @classmethod
    def from_model(
        cls,
        event: "Event",
        current_user: Optional["User"] = None,
        session: Optional["Session"] = None,
    ) -> "EventRead":
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
                            Membership.organization_id == event.organization_id,
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
            OrganizationRead.from_model(org, session)
            for org in event.guest_organizations
        ]

        # Links
        links_read = (
            [
                EventLinkRead(id=l.id, name=l.name, url=l.url, order=l.order)
                for l in event.event_links
            ]
            if not should_hide
            else []
        )

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
                emoji=emoji, count=count, user_reacted=(emoji in user_reacted_emojis)
            )
            for emoji, count in reaction_counts.items()
        ]

        creator = None
        if session and event.created_by_id:
            creator_obj = session.get(User, event.created_by_id)
            if creator_obj:
                creator = UserPublicRead.from_model(creator_obj, session)

        group_read = None
        if event.group:
            group_read = GroupRead(id=event.group.id, name=event.group.name)

        poster_file = None
        if session and event.poster_file_id:
            from app.models import StoredFile

            sf = session.get(StoredFile, event.poster_file_id)
            if sf:
                poster_file = StoredFileRead.from_model(sf)

        video_file = None
        if session and event.video_file_id:
            from app.models import StoredFile

            sf = session.get(StoredFile, event.video_file_id)
            if sf:
                video_file = StoredFileRead.from_model(sf)

        # Ensure timezone context is preserved/added
        start_time = (
            event.start_time.replace(tzinfo=timezone.utc)
            if event.start_time.tzinfo is None
            else event.start_time
        )
        end_time = (
            event.end_time.replace(tzinfo=timezone.utc)
            if event.end_time.tzinfo is None
            else event.end_time
        )

        return cls(
            id=event.id,
            title=event.title,
            description=None if should_hide else event.description,
            start_time=start_time,
            end_time=end_time,
            location=None if should_hide else event.location,
            location_url=None if should_hide else event.location_url,
            visibility=event.visibility,
            hide_details=event.hide_details,
            poster_url=(
                None if should_hide else (poster_file.url if poster_file else None)
            ),
            video_url=None if should_hide else (video_file.url if video_file else None),
            submitted_at=event.submitted_at,
            created_at=event.created_at,
            featured=event.featured,
            is_featured=(
                event.featured > 0
                and start_time.replace(tzinfo=timezone.utc)
                <= (datetime.now(timezone.utc) + timedelta(days=event.featured))
            ),
            approved_at=event.approved_at,
            rejection_message=(
                event.rejection_message
                if (
                    current_user
                    and (
                        current_user.id == event.created_by_id
                        or current_user.is_superadmin
                    )
                )
                else None
            ),
            organization=(
                OrganizationRead.from_model(event.organization, session)
                if event.organization
                else None
            ),
            guest_organizations=guest_orgs_read,
            tags=tags_read,
            event_links=links_read,
            group=group_read,
            created_by=creator,
            created_by_id=event.created_by_id,
            reactions=reactions_summary,
            is_draft=(event.visibility == EventVisibility.DRAFT),
            poster_file=poster_file,
            video_file=video_file,
        )


class ShortLinkCreate(BaseModel):
    item_type: str
    item_id: str
    action_type: str


class ShortLinkRead(BaseModel):
    id: str
    url: str


class ShortLinkInfo(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    item_type: str
    item_id: UUID
    logo_url: Optional[str] = None
    logo_file: Optional[StoredFileRead] = None
    color_primary: Optional[str] = None
    color_secondary: Optional[str] = None
    color_dark: Optional[str] = None
    tag_color: Optional[str] = None


class Message(BaseModel):
    message: str


# ---------------------------------------------------------------------------
# HelloAsso schemas
# ---------------------------------------------------------------------------


class HelloAssoStatus(BaseModel):
    connected: bool
    helloasso_slug: Optional[str] = None
    api_client_id: Optional[str] = None  # Shown to admins; secret is never returned
    can_manage_payment_forms: bool = False


class HelloAssoFormSummary(BaseModel):
    """A HelloAsso form as returned by the HA forms list API."""

    form_type: str
    form_slug: str
    title: str
    state: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class BilleterieCreate(BaseModel):
    """Request body for linking a HelloAsso billeterie to a payment form."""

    org_id: UUID  # The organization that directly has HA configured
    form_slug: str
    form_type: str = "Event"
    form_title: str


class BilleterieRead(BaseModel):
    """Billeterie link as returned by the API."""

    id: UUID
    helloasso_org_id: UUID
    helloasso_form_slug: str
    helloasso_form_title: str
    helloasso_form_type: str
    last_imported_at: Optional[datetime] = None
    created_at: datetime


class BilleterieImportResult(BaseModel):
    """Result of a billeterie attendee import."""

    imported: int
    skipped: int


class HelloAssoCredentials(BaseModel):
    """Write-only: set/update API credentials for an organization."""

    helloasso_slug: str
    api_client_id: str
    api_client_secret: str  # Accepted but never returned after storage


class PaymentFormOption(BaseModel):
    id: Optional[UUID] = None  # set when reading from DB; omit when creating
    name: str
    price_cents: int
    is_private: bool = False
    allowed_user_ids: List[str] = []


class PaymentFormCreate(BaseModel):
    total_amount_cents: int
    item_name: str
    options: List[PaymentFormOption] = []


class PaymentFormUpdate(BaseModel):
    """Partial update for an existing payment form."""

    item_name: Optional[str] = None
    total_amount_cents: Optional[int] = None
    options: Optional[List[PaymentFormOption]] = None
    is_open: Optional[bool] = None


class PaymentFormRead(BaseModel):
    id: UUID
    event_id: UUID
    requesting_org_id: UUID
    approving_org_id: Optional[UUID] = None
    total_amount_cents: int
    item_name: str
    status: PaymentFormStatus
    options: List[PaymentFormOption] = []
    is_open: bool = True
    rejection_message: Optional[str] = None
    payment_completed: bool
    entry_count: int = 0
    completed_count: int = 0
    created_by_id: UUID
    reviewed_by_id: Optional[UUID] = None
    created_at: datetime
    reviewed_at: Optional[datetime] = None
    billeterie: Optional[BilleterieRead] = None


class PaymentInitiateRequest(BaseModel):
    """Optional add-on options selected by the user before paying."""

    selected_option_ids: List[str] = []  # UUIDs of chosen EventPaymentFormOption rows


class PaymentInitiateResponse(BaseModel):
    """Returned when a user initiates payment — contains the HelloAsso redirect URL."""

    redirect_url: str
    checkout_intent_id: str


class PaymentCheckResult(BaseModel):
    """Result of polling HelloAsso for pending payment entries."""

    checked: int
    completed: int
    backfilled: int = 0


class ImportedOption(BaseModel):
    """An option as imported from a HelloAsso billeterie item."""

    name: str
    amount_cents: int


class PaymentEntryRead(BaseModel):
    id: UUID
    user_id: Optional[UUID] = None
    user_name: Optional[str] = None
    attendee_name: Optional[str] = None
    checkout_intent_id: Optional[str] = None
    helloasso_payment_id: Optional[str] = None
    helloasso_order_id: Optional[str] = None
    amount_cents: int
    payment_type: str = "helloasso"
    selected_option_ids: List[str] = []  # UUIDs of chosen EventPaymentFormOption rows
    imported_options: List[ImportedOption] = []
    completed: bool
    completed_at: Optional[datetime] = None
    cancelled: bool = False
    cancelled_at: Optional[datetime] = None
    created_at: datetime


class PaymentDashboardItem(BaseModel):
    """Aggregated view of a payment form for the dashboard."""

    id: UUID
    event_id: UUID
    event_title: str
    event_start_time: datetime
    org_id: UUID
    org_name: str
    approving_org_id: Optional[UUID] = None
    item_name: str
    total_amount_cents: int
    options: List[PaymentFormOption] = []
    status: PaymentFormStatus
    is_open: bool
    entry_count: int
    completed_count: int
    baseline_total_amount_cents: int = 0
    baseline_participant_count: int = 0
    created_at: datetime
    billeterie: Optional[BilleterieRead] = None


class PaymentFormReject(BaseModel):
    rejection_message: str


class MyPaymentEntryRead(BaseModel):
    """A user's own payment entry, enriched with event and form details."""

    id: UUID
    event_id: UUID
    event_title: str
    event_start_time: datetime
    org_name: str
    item_name: str
    amount_cents: int
    payment_type: str = "helloasso"
    selected_options: List[PaymentFormOption] = []
    completed: bool
    created_at: datetime


class ValidationEntryRead(BaseModel):
    """Entry as shown on the ticket-validation page."""

    id: UUID
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    attendee_name: Optional[str] = None
    display_name: str  # user_name or attendee_name fallback
    item_name: str
    amount_cents: int
    payment_type: str
    selected_options: List[PaymentFormOption] = []
    imported_options: List[ImportedOption] = []
    completed: bool
    validated: bool
    validated_at: Optional[datetime] = None
    cancelled: bool = False
    created_at: datetime


class ManualEntryCreate(BaseModel):
    attendee_name: str
    payment_type: PaymentType = PaymentType.CASH
    amount_cents: Optional[int] = None  # defaults to form base price
    selected_option_ids: List[str] = []  # UUIDs of chosen EventPaymentFormOption rows
    note: Optional[str] = None


class AttendeeSearchResult(BaseModel):
    """A candidate person for manual entry autocomplete."""

    id: Optional[UUID] = None  # None for LDAP-only users
    full_name: Optional[str] = None
    email: Optional[str] = None
    uid: Optional[str] = None  # LDAP uid / login
    source: str  # "user" | "ldap"


class BulkResolveRequest(BaseModel):
    queries: List[str]


class UserBatchLookupRequest(BaseModel):
    ids: List[str]


class BulkResolveResult(BaseModel):
    query: str
    user_id: Optional[str] = None  # UUID as string
    full_name: Optional[str] = None


class ChangelogEntryRead(BaseModel):
    id: UUID
    title: str
    content: str
    audience: ChangelogAudience
    image_urls: Optional[List[str]] = None
    created_at: datetime


class ChangelogEntryCreate(BaseModel):
    title: str
    content: str
    audience: ChangelogAudience = ChangelogAudience.ALL
    image_urls: Optional[List[str]] = None


class ChangelogEntryUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    audience: Optional[ChangelogAudience] = None
    image_urls: Optional[List[str]] = None
