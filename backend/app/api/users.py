from typing import Any, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlmodel import Session, col, or_, select, func
from starlette.config import Config

from app.api.auth import get_current_user
from app.database import get_session
from app.models import (
    Event,
    EventReaction,
    Group,
    GroupMembership,
    Membership,
    Organization,
    Role,
    Subscription,
    User,
    UserLink,
)
from app.schemas import (
    UserPublicRead,
    UserRead,
    PaginatedResponse,
    UserLinkRead,
    UserLinkCreate,
)
from app.utils.email import send_email

router = APIRouter()
config = Config(".env")


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    profile_picture_file_id: Optional[str] = None  # UUID string
    phone_number: Optional[str] = None


class UserInvite(BaseModel):
    email: str


class UserSearchResult(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None

    class Config:
        from_attributes = True


class MembershipWithOrganization(BaseModel):
    id: str
    user_id: str
    organization_id: str
    role: str
    title: Optional[str] = None
    organization: Optional[Any] = None  # OrganizationRead at runtime


@router.get("/me/organizations")
async def get_user_organizations(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get all organizations where the current user is a member (any role)"""
    from app.schemas import OrganizationRead

    memberships = session.exec(
        select(Membership).where(Membership.user_id == current_user.id)
    ).all()

    return [
        OrganizationRead.from_model(m.organization, session, m) for m in memberships
    ]


@router.get("/me/memberships")
async def get_user_memberships(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get all memberships for the current user with organization details"""
    from app.schemas import OrganizationRead

    memberships = session.exec(
        select(Membership).where(Membership.user_id == current_user.id)
    ).all()

    result = []
    for membership in memberships:
        org = membership.organization
        result.append(
            MembershipWithOrganization(
                id=str(membership.id),
                user_id=str(membership.user_id),
                organization_id=str(membership.organization_id),
                role=membership.role.value,
                title=membership.title,
                organization=OrganizationRead.from_model(org, session) if org else None,
            )
        )

    return result


@router.get("/me/groups")
async def get_user_groups(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get all groups for the current user"""
    memberships = session.exec(
        select(GroupMembership).where(GroupMembership.user_id == current_user.id)
    ).all()

    result = []
    for membership in memberships:
        group = membership.group
        if group:
            # We also want organization info for display
            organization = session.get(Organization, group.organization_id)
            if organization:
                result.append(
                    {
                        "id": str(group.id),
                        "name": group.name,
                        "description": group.description,
                        "organization": {
                            "id": str(organization.id),
                            "name": organization.name,
                        },
                        "membership_id": str(membership.id),
                        "joined_at": membership.joined_at.isoformat(),
                    }
                )

    return result


@router.get("/{user_id}/memberships", response_model=List[MembershipWithOrganization])
async def get_other_user_memberships(
    user_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get memberships for a specific user"""
    # Allow if superadmin or if requesting own memberships
    if not current_user.is_superadmin and str(current_user.id) != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    memberships = session.exec(
        select(Membership).where(Membership.user_id == UUID(user_id))
    ).all()

    from app.schemas import OrganizationRead

    result = []
    for membership in memberships:
        org = membership.organization
        result.append(
            MembershipWithOrganization(
                id=str(membership.id),
                user_id=str(membership.user_id),
                organization_id=str(membership.organization_id),
                role=membership.role.value,
                title=membership.title,
                organization=OrganizationRead.from_model(org, session) if org else None,
            )
        )

    return result


@router.put("/me", response_model=UserRead)
async def update_user_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Update current user's profile"""
    user = session.get(User, current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update fields if provided
    if user_data.full_name is not None:
        user.full_name = user_data.full_name
    if user_data.profile_picture_file_id is not None:
        from uuid import UUID as _UUID

        user.profile_picture_file_id = _UUID(user_data.profile_picture_file_id)
    if user_data.phone_number is not None:
        user.phone_number = user_data.phone_number

    session.add(user)
    session.commit()
    session.refresh(user)

    return _user_read(user, session)


# --- User Links and helpers ---


def _user_read(user: User, session: Session) -> UserRead:
    """Build a UserRead response with eagerly-loaded links and profile picture."""
    from app.models import StoredFile
    from app.schemas import StoredFileRead

    links = session.exec(
        select(UserLink)
        .where(UserLink.user_id == user.id)
        .order_by(col(UserLink.order))
    ).all()
    profile_picture_file = None
    if user.profile_picture_file_id:
        sf = session.get(StoredFile, user.profile_picture_file_id)
        if sf:
            profile_picture_file = StoredFileRead.from_model(sf)
    return UserRead(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        profile_picture_url=profile_picture_file.url if profile_picture_file else None,
        phone_number=user.phone_number,
        is_superadmin=user.is_superadmin,
        exempt_from_rgpd_delete=user.exempt_from_rgpd_delete,
        is_active=user.is_active,
        notification_delay=user.notification_delay,
        links=[
            UserLinkRead(id=l.id, name=l.name, url=l.url, order=l.order) for l in links
        ],
        profile_picture_file=profile_picture_file,
    )


@router.get("/me/links", response_model=List[UserLinkRead])
async def list_my_links(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    links = session.exec(
        select(UserLink)
        .where(UserLink.user_id == current_user.id)
        .order_by(col(UserLink.order))
    ).all()
    return links


@router.get("/{user_id}/links", response_model=List[UserLinkRead])
async def list_user_links(
    user_id: str,
    session: Session = Depends(get_session),
):
    """Public endpoint – no auth required"""
    uid = UUID(user_id)
    links = session.exec(
        select(UserLink).where(UserLink.user_id == uid).order_by(col(UserLink.order))
    ).all()
    return links


@router.post("/me/links", response_model=UserLinkRead)
async def create_my_link(
    link_data: UserLinkCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    from uuid import uuid4

    link = UserLink(
        id=uuid4(),
        user_id=current_user.id,
        name=link_data.name,
        url=link_data.url,
        order=link_data.order,
    )
    session.add(link)
    session.commit()
    session.refresh(link)
    return link


@router.put("/me/links/{link_id}", response_model=UserLinkRead)
async def update_my_link(
    link_id: str,
    link_data: UserLinkCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    link = session.get(UserLink, UUID(link_id))
    if not link or link.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Lien introuvable")
    link.name = link_data.name
    link.url = link_data.url
    link.order = link_data.order
    session.add(link)
    session.commit()
    session.refresh(link)
    return link


@router.delete("/me/links/{link_id}")
async def delete_my_link(
    link_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    link = session.get(UserLink, UUID(link_id))
    if not link or link.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Lien introuvable")
    session.delete(link)
    session.commit()
    return {"ok": True}


@router.get("/search", response_model=List[UserSearchResult])
async def search_users(
    q: str = Query(..., min_length=1, description="Search query"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Search users by name or email"""
    search_pattern = f"%{q}%"

    users = session.exec(
        select(User)
        .where(
            or_(
                User.full_name.ilike(search_pattern),  # pyright: ignore
                User.email.ilike(search_pattern),  # pyright: ignore
            )
        )
        .limit(20)
    ).all()

    return [
        UserSearchResult(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
        )
        for user in users
    ]


@router.get("/{user_id}", response_model=UserRead)
async def get_user_profile(
    user_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get a user's public profile by ID"""
    if user_id == "me":
        return _user_read(current_user, session)

    user = session.get(User, UUID(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return _user_read(user, session)


@router.get("/", response_model=PaginatedResponse[UserRead])
async def list_users(
    page: int = 1,
    size: int = 50,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """List all users (Superadmin only)"""
    if not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Not authorized")

    query = select(User)

    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                User.full_name.ilike(search_pattern),  # pyright: ignore
                User.email.ilike(search_pattern),  # pyright: ignore
            )
        )

    # Sort by name (full_name) then email
    # Handle potentially None full_name by using email as fallback for sorting logic if needed,
    # but simple order_by is usually enough. Postgres sorts NULLs last by default usually.
    query = query.order_by(User.full_name, User.email)  # pyright: ignore

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = session.exec(count_query).one()

    # Pagination
    users = session.exec(query.offset((page - 1) * size).limit(size)).all()
    pages = (total + size - 1) // size if size > 0 else 0

    return PaginatedResponse(
        items=[_user_read(u, session) for u in users],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.post("/invite", response_model=UserRead)
async def invite_user(
    invite: UserInvite,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Invite a new user (Superadmin only)"""
    if not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Only superadmins can invite users")

    existing = session.exec(select(User).where(User.email == invite.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    user = User(
        email=invite.email,
        full_name=None,  # Will be filled on first OIDC login
        is_active=True,
        is_superadmin=False,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Send email
    app_url = config.get("APP_BASE_URL")

    html_content = f"""
    <h1>Invitation Calend'INT!</h1>
    <p>Vous avez été invité à rejoindre Calend'INT.</p>
    <p>Veuillez vous connecter pour configurer votre compte: <a href="{app_url}/login">{app_url}/login</a></p>
    """
    try:
        send_email(user.email, "Calend'INT by MiNET", html_content)
    except Exception as e:
        print(f"Error sending email: {e}")

    return user


@router.put("/{user_id}/superadmin", response_model=UserRead)
async def toggle_superadmin(
    user_id: str,
    is_superadmin: bool,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
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


@router.put("/{user_id}/exempt-ldap", response_model=UserRead)
async def toggle_exempt_from_rgpd_delete(
    user_id: str,
    exempt: bool,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Toggle exempt from LDAP sync status (Superadmin only)"""
    if not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Not authorized")

    user = session.get(User, UUID(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.exempt_from_rgpd_delete = exempt
    session.add(user)
    session.commit()
    session.refresh(user)

    return user


@router.put("/{user_id}/active", response_model=UserRead)
async def toggle_active(
    user_id: str,
    is_active: bool,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
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
    session: Session = Depends(get_session),
):
    """Delete a user"""
    from app.models import (
        EventPaymentEntry,
        EventPaymentForm,
        GHOST_USER_ID,
        OrganizationHelloAsso,
        PaymentFormBilleterie,
        ShortLink,
        StoredFile,
        UserPushToken,
    )

    if not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Not authorized")

    user = session.get(User, UUID(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Prevent deleting yourself
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")

    # Replace/delete everything that mentions the user

    # 1. Memberships
    memberships = session.exec(
        select(Membership).where(Membership.user_id == user.id)
    ).all()
    for m in memberships:
        session.delete(m)

    # 2. Group Memberships
    group_memberships = session.exec(
        select(GroupMembership).where(GroupMembership.user_id == user.id)
    ).all()
    for gm in group_memberships:
        session.delete(gm)

    # 3. Subscriptions (This was the cause of the reported error)
    subscriptions = session.exec(
        select(Subscription).where(Subscription.user_id == user.id)
    ).all()
    for s in subscriptions:
        session.delete(s)

    # 4. Event Reactions
    reactions = session.exec(
        select(EventReaction).where(EventReaction.user_id == user.id)
    ).all()
    for r in reactions:
        session.delete(r)

    # 5. Events created by user
    events = session.exec(select(Event).where(Event.created_by_id == user.id)).all()
    for e in events:
        e.created_by_id = GHOST_USER_ID
        session.add(e)

    # 6. ShortLinks created by user
    shortlinks = session.exec(
        select(ShortLink).where(ShortLink.created_by_id == user.id)
    ).all()
    for sl in shortlinks:
        sl.created_by_id = GHOST_USER_ID
        session.add(sl)

    # 7. Payment entries: keep rows, replace the user with ghost
    payment_entries = session.exec(
        select(EventPaymentEntry).where(EventPaymentEntry.user_id == user.id)
    ).all()
    for pe in payment_entries:
        pe.user_id = GHOST_USER_ID
        session.add(pe)

    # 8. Entries validated by this user
    validated_entries = session.exec(
        select(EventPaymentEntry).where(EventPaymentEntry.validated_by_id == user.id)
    ).all()
    for pe in validated_entries:
        pe.validated_by_id = None
        session.add(pe)

    # 9. Payment forms
    forms_created = session.exec(
        select(EventPaymentForm).where(EventPaymentForm.created_by_id == user.id)
    ).all()
    for form in forms_created:
        form.created_by_id = GHOST_USER_ID
        session.add(form)

    forms_reviewed = session.exec(
        select(EventPaymentForm).where(EventPaymentForm.reviewed_by_id == user.id)
    ).all()
    for form in forms_reviewed:
        form.reviewed_by_id = None
        session.add(form)

    billeteries = session.exec(
        select(PaymentFormBilleterie).where(
            PaymentFormBilleterie.created_by_id == user.id
        )
    ).all()
    for b in billeteries:
        b.created_by_id = GHOST_USER_ID
        session.add(b)

    ha_conns = session.exec(
        select(OrganizationHelloAsso).where(
            OrganizationHelloAsso.connected_by_id == user.id
        )
    ).all()
    for ha in ha_conns:
        ha.connected_by_id = GHOST_USER_ID
        session.add(ha)

    uploaded_files = session.exec(
        select(StoredFile).where(StoredFile.uploaded_by_id == user.id)
    ).all()
    for sf in uploaded_files:
        sf.uploaded_by_id = GHOST_USER_ID
        session.add(sf)

    # 10. User Links
    user_links = session.exec(select(UserLink).where(UserLink.user_id == user.id)).all()
    for ul in user_links:
        session.delete(ul)

    # 11. Push Tokens
    push_tokens = session.exec(
        select(UserPushToken).where(UserPushToken.user_id == user.id)
    ).all()
    for pt in push_tokens:
        session.delete(pt)

    session.delete(user)
    session.commit()

    return {"ok": True}
