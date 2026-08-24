from datetime import datetime
import os
import ssl
from typing import List
from uuid import UUID, uuid4

from fastapi import APIRouter, Body, Depends, HTTPException
from ldap3 import ALL, Connection, SUBTREE, Server, Tls
from pydantic import BaseModel
from sqlmodel import Session, col, delete, select

from app.api.auth import get_current_user
from app.database import get_session
from app.member_visibility import normalize_student_year
from app.models import (
    EventPaymentEntry,
    EventPaymentForm,
    EventReaction,
    GroupMembership,
    LDAPUser,
    Membership,
    OrganizationHelloAsso,
    PaymentFormBilleterie,
    ShortLink,
    StoredFile,
    Subscription,
    User,
    GHOST_USER_ID,
)
from app.schemas import UserRead

router = APIRouter()
LDAP_STUDENT_YEAR_ATTRIBUTE = "supannEtuEtape"


class LDAPSyncRequest(BaseModel):
    username: str
    password: str


class LDAPUserRead(BaseModel):
    id: str
    email: str
    full_name: str | None
    uid: str | None
    student_year: int | None


@router.post("/ldap/sync")
async def sync_ldap_users(
    creds: LDAPSyncRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Sync users from LDAP to local cache table (Superadmin only)"""
    if not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Superadmin access required")

    ldap_host = os.getenv("LDAP_HOST", "ldapha.imtbs-tsp.eu")
    ldap_port = int(os.getenv("LDAP_PORT", "636"))
    base_dn = os.getenv("LDAP_BASE_DN", "ou=active,dc=int-evry,dc=fr")
    bind_dn = os.getenv("LDAP_BIND_DN", "")
    ignore_certs = os.getenv("LDAP_IGNORE_CERTS", "true").lower() in (
        "true",
        "1",
        "yes",
        "y",
    )
    ldap_filter = os.getenv("LDAP_FILTER", "(&(objectClass=person)(mail=*))")
    # Construct User DN
    user_dn = f"uid={creds.username},{bind_dn}"

    try:
        if ignore_certs:
            tls = Tls(
                validate=ssl.CERT_NONE,
                version=ssl.PROTOCOL_TLS_CLIENT,
                ciphers="ALL:@SECLEVEL=1",
            )
        else:
            tls = Tls(validate=ssl.CERT_REQUIRED)

        print("Ignore certs:", ignore_certs)
        server = Server(ldap_host, port=ldap_port, use_ssl=True, get_info=ALL, tls=tls)
        conn = Connection(server, user=user_dn, password=creds.password, auto_bind=True)

        if not conn.bound:
            raise HTTPException(status_code=401, detail="LDAP Authentication failed")

        # Search for valid users (usually have mail)
        conn.search(
            search_base=base_dn,
            search_filter=ldap_filter,
            search_scope=SUBTREE,
            attributes=[
                "mail",
                "cn",
                "displayName",
                "uid",
                "givenName",
                "sn",
                LDAP_STUDENT_YEAR_ATTRIBUTE,
            ],
        )

        entries = conn.entries

        # Clear existing table
        # Note: SQLModel doesn't directly support `session.exec(delete(Model))` identically to select sometimes,
        # but SQLAlchemy delete object works.
        stmt = delete(LDAPUser)
        session.exec(stmt)  # pyright: ignore
        session.commit()

        new_users = []
        for entry in entries:
            # ldap3 attributes are dynamically valid
            mail_val = (
                entry.mail.value if hasattr(entry.mail, "value") else str(entry.mail)
            )
            if not mail_val:
                continue

            uid_val = None
            if hasattr(entry, "uid") and entry.uid:
                uid_val = (
                    entry.uid.value if hasattr(entry.uid, "value") else str(entry.uid)
                )

            # Helper for name
            full_name = None
            if hasattr(entry, "displayName") and entry.displayName:
                full_name = str(entry.displayName)
            elif hasattr(entry, "cn") and entry.cn:
                full_name = str(entry.cn)

            ldap_user = LDAPUser(
                id=uuid4(),
                email=str(mail_val),
                full_name=full_name,
                uid=str(uid_val),
                student_year=normalize_student_year(
                    entry[LDAP_STUDENT_YEAR_ATTRIBUTE].values
                    if LDAP_STUDENT_YEAR_ATTRIBUTE in entry.entry_attributes
                    else None
                ),
                synced_at=datetime.now(),
            )
            new_users.append(ldap_user)

        session.add_all(new_users)
        session.commit()

        return {"message": f"Successfully synced {len(new_users)} users from LDAP"}

    except Exception as e:
        print(f"LDAP Error: {e}")
        # If it's an auth error from ldap3, typically it raises
        if "invalidCredentials" in str(e):
            raise HTTPException(status_code=401, detail="Identifiants LDAP invalides")
        raise HTTPException(status_code=500, detail=f"LDAP Sync failed: {str(e)}")


@router.get("/ldap/users", response_model=List[LDAPUserRead])
async def search_ldap_users(
    q: str = "",
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Search users in the LDAP cache"""
    if not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Superadmin access required")

    query = select(LDAPUser)
    if q:
        search_pattern = f"%{q}%"
        query = query.where(
            (col(LDAPUser.full_name).ilike(search_pattern))
            | (col(LDAPUser.email).ilike(search_pattern))
            | (col(LDAPUser.uid).ilike(search_pattern))
        )

    query = query.limit(50)
    users = session.exec(query).all()

    return [
        LDAPUserRead(
            id=str(u.id),
            email=u.email,
            full_name=u.full_name,
            uid=u.uid,
            student_year=u.student_year,
        )
        for u in users
    ]


def _delete_user_with_aggregation(user: User, session: Session) -> None:
    """Remove a user account while preserving payment-entry history.

    EventPaymentEntry rows are reassigned to GHOST_USER_ID so participant and
    revenue history stay visible in payment tables and exports.
    """
    user_id = user.id

    # 1. Reassign payment entries to ghost user (keep payment history)
    entries = session.exec(
        select(EventPaymentEntry).where(EventPaymentEntry.user_id == user_id)
    ).all()
    for entry in entries:
        entry.user_id = GHOST_USER_ID
        session.add(entry)

    # 2. Clear validated_by_id on entries this user validated
    for entry in session.exec(
        select(EventPaymentEntry).where(EventPaymentEntry.validated_by_id == user_id)
    ).all():
        entry.validated_by_id = None
        session.add(entry)

    # 3. Payment forms: reassign created_by → ghost; clear reviewed_by
    for form in session.exec(
        select(EventPaymentForm).where(EventPaymentForm.created_by_id == user_id)
    ).all():
        form.created_by_id = GHOST_USER_ID
        session.add(form)
    for form in session.exec(
        select(EventPaymentForm).where(EventPaymentForm.reviewed_by_id == user_id)
    ).all():
        form.reviewed_by_id = None
        session.add(form)

    # 4. Billeterie created_by → ghost
    for b in session.exec(
        select(PaymentFormBilleterie).where(
            PaymentFormBilleterie.created_by_id == user_id
        )
    ).all():
        b.created_by_id = GHOST_USER_ID
        session.add(b)

    # 5. Delete group memberships, subscriptions, reactions, short links
    for gm in session.exec(
        select(GroupMembership).where(GroupMembership.user_id == user_id)
    ).all():
        session.delete(gm)
    for sub in session.exec(
        select(Subscription).where(Subscription.user_id == user_id)
    ).all():
        session.delete(sub)
    for rx in session.exec(
        select(EventReaction).where(EventReaction.user_id == user_id)
    ).all():
        session.delete(rx)
    for sl in session.exec(
        select(ShortLink).where(ShortLink.created_by_id == user_id)
    ).all():
        session.delete(sl)

    # 6. HelloAsso credentials connected_by → ghost
    for ha in session.exec(
        select(OrganizationHelloAsso).where(
            OrganizationHelloAsso.connected_by_id == user_id
        )
    ).all():
        ha.connected_by_id = GHOST_USER_ID
        session.add(ha)

    # 7. Uploaded files → ghost
    for sf in session.exec(
        select(StoredFile).where(StoredFile.uploaded_by_id == user_id)
    ).all():
        sf.uploaded_by_id = GHOST_USER_ID
        session.add(sf)

    # 8. Memberships
    for m in session.exec(
        select(Membership).where(Membership.user_id == user_id)
    ).all():
        session.delete(m)

    # 9. Delete the user (cascade removes push_tokens and UserLinks)
    session.delete(user)


@router.post("/housekeeping")
async def housekeeping(
    delete_orphan_users: bool = False,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Trigger housekeeping tasks (superadmin only).

    - Always: delete organizations whose delete_after date has passed.
    - delete_orphan_users=true: also delete user accounts that are no longer
      present in the LDAP cache and are not exempt from RGPD deletion.
            Payment entries are reassigned to the ghost user to preserve history.
    """
    from datetime import datetime, timezone
    from app.models import Organization, GHOST_USER_ID as _ghost
    from app.api.organizations import delete_organization

    if not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Superadmin access required")

    now = datetime.now(timezone.utc)

    # --- Org cleanup ---
    orgs_to_delete = session.exec(
        select(Organization).where(
            Organization.delete_after != None, col(Organization.delete_after) <= now
        )
    ).all()

    org_count = 0
    org_errors = 0
    for org in orgs_to_delete:
        try:
            delete_organization(str(org.id), current_user, session)
            org_count += 1
        except Exception as e:
            print(f"Error deleting org {org.id}: {e}")
            org_errors += 1

    # --- Orphan user deletion ---
    user_count = 0
    user_errors = 0
    if delete_orphan_users:
        ldap_count = session.exec(select(LDAPUser)).all()
        if ldap_count:
            subq_email = select(LDAPUser.email)
            orphans = session.exec(
                select(User).where(
                    User.email.notin_(subq_email),  # pyright: ignore
                    User.exempt_from_rgpd_delete == False,
                    User.id != _ghost,
                    User.id != current_user.id,
                )
            ).all()
            for user in orphans:
                try:
                    _delete_user_with_aggregation(user, session)
                    user_count += 1
                except Exception as e:
                    print(f"Error deleting user {user.id}: {e}")
                    user_errors += 1
            session.commit()

    msg = f"Housekeeping complete. Orgs deleted: {org_count} (errors: {org_errors})."
    if delete_orphan_users:
        msg += f" Users deleted: {user_count} (errors: {user_errors})."
    return {"message": msg}


@router.post("/mandate-reminders/send")
async def send_mandate_reminders(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Email every org-admin who has held their post for more than 8 months, with a link
    to the passation page for each organization they administer (superadmin only)."""
    from collections import defaultdict
    from datetime import timedelta, timezone

    from app.email.utils import render_email_template, send_email
    from app.models import Organization, Role

    if not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Superadmin access required")

    threshold = datetime.now(timezone.utc) - timedelta(days=8 * 30)

    stale_admins = session.exec(
        select(Membership).where(
            Membership.role == Role.ORG_ADMIN,
            col(Membership.created_at) <= threshold,
        )
    ).all()

    orgs_by_user: dict[UUID, list[Organization]] = defaultdict(list)
    for membership in stale_admins:
        org = session.get(Organization, membership.organization_id)
        if org:
            orgs_by_user[membership.user_id].append(org)

    app_base_url = os.getenv("APP_BASE_URL", "https://cal.minet.net")
    sent = 0
    for user_id, orgs in orgs_by_user.items():
        user = session.get(User, user_id)
        if not user:
            continue
        html_content = render_email_template(
            "mandate_reminder.html",
            {
                "project_name": "Calend'INT",
                "year": datetime.now(timezone.utc).year,
                "user_name": user.full_name or user.email,
                "organizations": [
                    {
                        "name": org.name,
                        "transfer_url": f"{app_base_url}/organizations/{org.id}/members#mandate",
                    }
                    for org in orgs
                ],
            },
        )
        send_email(user.email, "Rappel : pensez à la passation de votre mandat", html_content)
        sent += 1

    return {"message": "reminders_sent", "count": sent}


@router.get("/ldap/orphans", response_model=List[UserRead])
async def get_ldap_orphaned_users(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Retrieve users absent from LDAP cache that are not exempt"""
    from app.models import GHOST_USER_ID, LDAPUser
    from sqlmodel import func

    if not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Superadmin access required")

    ldap_count = session.exec(select(func.count(col(LDAPUser.id)))).first()
    if not ldap_count:
        return []

    subq_email = select(LDAPUser.email)

    orphans = session.exec(
        select(User).where(
            User.email.notin_(subq_email),  # pyright: ignore
            User.exempt_from_rgpd_delete == False,
            User.id != GHOST_USER_ID,
        )
    ).all()

    return [u for u in orphans]
