"""HelloAsso integration: API credentials management, payment form proposals,
approval workflow, on-demand checkout intent creation, and incoming payment webhooks.
"""

import hashlib
import hmac
import json as _json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from jinja2 import Environment, FileSystemLoader
import unicodedata

from sqlmodel import Session, col, or_, select

from app.api.auth import get_current_user
from app.database import engine, get_session
from app.models import (
    Event,
    EventPaymentEntry,
    EventPaymentForm,
    LDAPUser,
    Membership,
    Organization,
    OrganizationHelloAsso,
    PaymentFormStatus,
    Role,
    User,
)
from app.schemas import (
    AttendeeSearchResult,
    HelloAssoCredentials,
    HelloAssoStatus,
    ManualEntryCreate,
    MyPaymentEntryRead,
    PaymentDashboardItem,
    PaymentEntryRead,
    PaymentFormCreate,
    PaymentFormOption,
    PaymentFormRead,
    PaymentFormReject,
    PaymentFormUpdate,
    PaymentInitiateRequest,
    PaymentInitiateResponse,
    ValidationEntryRead,
    BulkResolveRequest,
    BulkResolveResult,
)
from app.services import helloasso as ha_service
from app.utils.email import send_email
from sqlmodel import Session as DBSession

router = APIRouter()
webhooks_router = APIRouter()
logger = logging.getLogger(__name__)


def _app_base_url() -> str:
    return os.getenv("APP_BASE_URL", "http://localhost")


def _helloasso_redirect_base_url() -> str:
    """Public base URL used for HelloAsso redirect fields (backUrl/returnUrl/errorUrl).
    Falls back to APP_BASE_URL. Must be a publicly reachable HTTPS URL."""
    return os.getenv("HELLOASSO_REDIRECT_BASE_URL") or _app_base_url()


_TEMPLATE_DIR = Path(__file__).parent.parent / "email" / "templates"


def _get_jinja_env() -> Environment:
    return Environment(loader=FileSystemLoader(str(_TEMPLATE_DIR)))


# ---------------------------------------------------------------------------
# Permission helpers
# ---------------------------------------------------------------------------


def _require_org_admin(org_id: UUID, current_user: User, session: Session) -> None:
    if current_user.is_superadmin:
        return
    membership = session.exec(
        select(Membership).where(
            Membership.user_id == current_user.id,
            Membership.organization_id == org_id,
            Membership.role == Role.ORG_ADMIN,
        )
    ).first()
    if not membership:
        raise HTTPException(status_code=403, detail="Not authorized")


def _can_propose_payment_form(
    event: Event, current_user: User, session: Session
) -> bool:
    if current_user.is_superadmin:
        return True
    membership = session.exec(
        select(Membership).where(
            Membership.user_id == current_user.id,
            Membership.organization_id == event.organization_id,
        )
    ).first()
    if not membership:
        return False
    return membership.role == Role.ORG_ADMIN or membership.can_manage_payment_forms


def _can_review_payment_form(
    form: EventPaymentForm, current_user: User, session: Session
) -> bool:
    if current_user.is_superadmin:
        return True
    if not form.approving_org_id:
        return False
    membership = session.exec(
        select(Membership).where(
            Membership.user_id == current_user.id,
            Membership.organization_id == form.approving_org_id,
            Membership.role == Role.ORG_ADMIN,
        )
    ).first()
    return membership is not None


def _can_manage_form(
    form: EventPaymentForm, current_user: User, session: Session
) -> bool:
    """Return True if user can edit or cancel this form (creator, org admin, or superadmin)."""
    if current_user.is_superadmin:
        return True
    if form.created_by_id == current_user.id:
        return True
    membership = session.exec(
        select(Membership).where(
            Membership.user_id == current_user.id,
            Membership.organization_id == form.requesting_org_id,
        )
    ).first()
    if not membership:
        return False
    return membership.role == Role.ORG_ADMIN or membership.can_manage_payment_forms


def _get_form_or_404(event_id: str, session: Session) -> EventPaymentForm:
    form = session.exec(
        select(EventPaymentForm).where(EventPaymentForm.event_id == UUID(event_id))
    ).first()
    if not form:
        raise HTTPException(status_code=404, detail="Payment form not found")
    return form


def _parse_options(raw: Optional[str]) -> List[PaymentFormOption]:
    if not raw:
        return []
    try:
        return [PaymentFormOption(**o) for o in _json.loads(raw)]
    except Exception:
        return []


def _to_read(
    form: EventPaymentForm, session: Optional[Session] = None
) -> PaymentFormRead:
    options = _parse_options(form.options)

    entry_count = 0
    completed_count = 0
    if session:
        entries = session.exec(
            select(EventPaymentEntry).where(
                EventPaymentEntry.payment_form_id == form.id
            )
        ).all()
        entry_count = len(entries)
        completed_count = sum(1 for e in entries if e.completed)

    return PaymentFormRead(
        id=form.id,
        event_id=form.event_id,
        requesting_org_id=form.requesting_org_id,
        approving_org_id=form.approving_org_id,
        total_amount_cents=form.total_amount_cents,
        item_name=form.item_name,
        status=form.status,
        options=options,
        is_open=form.is_open,
        rejection_message=form.rejection_message,
        payment_completed=form.payment_completed,
        entry_count=entry_count,
        completed_count=completed_count,
        created_by_id=form.created_by_id,
        reviewed_by_id=form.reviewed_by_id,
        created_at=form.created_at,
        reviewed_at=form.reviewed_at,
    )


# ---------------------------------------------------------------------------
# Background notification tasks
# ---------------------------------------------------------------------------


def _notify_parent_admins_of_pending_form(form_id: UUID, event_id: UUID) -> None:
    with DBSession(engine) as session:
        form = session.get(EventPaymentForm, form_id)
        event = session.get(Event, event_id)
        if not form or not event or not form.approving_org_id:
            return

        approving_org = session.get(Organization, form.approving_org_id)
        requesting_org = session.get(Organization, form.requesting_org_id)
        if not approving_org:
            return

        admins = session.exec(
            select(Membership).where(
                Membership.organization_id == form.approving_org_id,
                Membership.role == Role.ORG_ADMIN,
            )
        ).all()

        review_url = f"{_app_base_url()}/payments"
        env = _get_jinja_env()

        for admin_membership in admins:
            admin = session.get(User, admin_membership.user_id)
            if not admin or not admin.email:
                continue

            admin_name = admin.full_name or admin.email
            requesting_org_name = (
                requesting_org.name if requesting_org else "une organisation"
            )

            try:
                tmpl = env.get_template("helloasso_form_pending.html")
                html = tmpl.render(
                    project_name="Calend'INT",
                    year=datetime.now().year,
                    admin_name=admin_name,
                    event_title=event.title,
                    requesting_org_name=requesting_org_name,
                    item_name=form.item_name,
                    amount_euros=form.total_amount_cents / 100,
                    review_url=review_url,
                )
            except Exception:
                html = (
                    f"<p>Bonjour {admin_name},</p>"
                    f"<p>Un formulaire de paiement pour l'événement <strong>{event.title}</strong> "
                    f"({form.item_name}, {form.total_amount_cents / 100:.2f}\u00a0\u20ac) "
                    f"est en attente de votre validation.</p>"
                    f'<p><a href="{review_url}">Voir les formulaires en attente</a></p>'
                )

            send_email(
                email_to=admin.email,
                subject=f"Calend'INT \u2014 Formulaire de paiement en attente\u00a0: {event.title}",
                html_content=html,
            )


def _notify_creator(form_id: UUID, event_id: UUID, approved: bool) -> None:
    with DBSession(engine) as session:
        form = session.get(EventPaymentForm, form_id)
        event = session.get(Event, event_id)
        if not form or not event:
            return

        creator = session.get(User, form.created_by_id)
        if not creator or not creator.email:
            return

        creator_name = creator.full_name or creator.email
        event_url = f"{_app_base_url()}/events/{event.id}"
        env = _get_jinja_env()
        template_name = (
            "helloasso_form_approved.html"
            if approved
            else "helloasso_form_rejected.html"
        )

        try:
            tmpl = env.get_template(template_name)
            html = tmpl.render(
                project_name="Calend'INT",
                year=datetime.now().year,
                user_name=creator_name,
                event_title=event.title,
                item_name=form.item_name,
                rejection_message=form.rejection_message,
                event_url=event_url,
            )
        except Exception:
            if approved:
                html = (
                    f"<p>Bonjour {creator_name},</p>"
                    f"<p>Votre formulaire de paiement pour <strong>{event.title}</strong> a \u00e9t\u00e9 approuv\u00e9.</p>"
                    f'<p>Les participants peuvent maintenant payer depuis <a href="{event_url}">la page de l\'événement</a>.</p>'
                )
            else:
                html = (
                    f"<p>Bonjour {creator_name},</p>"
                    f"<p>Votre formulaire de paiement pour <strong>{event.title}</strong> a \u00e9t\u00e9 refus\u00e9.</p>"
                    f"<p>Motif\u00a0: {form.rejection_message}</p>"
                )

        subject = (
            f"Calend'INT \u2014 Formulaire de paiement approuv\u00e9\u00a0: {event.title}"
            if approved
            else f"Calend'INT \u2014 Formulaire de paiement refus\u00e9\u00a0: {event.title}"
        )
        send_email(email_to=creator.email, subject=subject, html_content=html)


# ---------------------------------------------------------------------------
# HelloAsso credentials management (write-only API key pair per org)
# ---------------------------------------------------------------------------


def _webhook_secret(org_id: str) -> str:
    """Compute the per-org webhook secret as HMAC-SHA256(SECRET_KEY, org_id)."""
    key = os.getenv("SECRET_KEY", "CHANGE_THIS_SECRET_KEY")
    return hmac.new(key.encode(), org_id.encode(), hashlib.sha256).hexdigest()


def _webhook_url(org_id: str) -> str:
    return (
        f"{_app_base_url()}/api/webhooks/helloasso/{org_id}/{_webhook_secret(org_id)}"
    )


@router.get("/status/{org_id}", response_model=HelloAssoStatus)
def helloasso_status(
    org_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    org_ha = session.exec(
        select(OrganizationHelloAsso).where(
            OrganizationHelloAsso.organization_id == UUID(org_id)
        )
    ).first()
    
    is_admin = current_user.is_superadmin
    if not is_admin:
        membership = session.exec(
            select(Membership).where(
                Membership.user_id == current_user.id,
                Membership.organization_id == UUID(org_id),
            )
        ).first()
        if membership and (
            membership.role == Role.ORG_ADMIN or membership.can_manage_payment_forms
        ):
            is_admin = True
            
    if not org_ha:
        return HelloAssoStatus(
            connected=False, 
            webhook_url=_webhook_url(org_id) if is_admin else None
        )
        
    return HelloAssoStatus(
        connected=True,
        helloasso_slug=org_ha.helloasso_slug if is_admin else None,
        api_client_id=org_ha.api_client_id if is_admin else None,
        webhook_url=_webhook_url(org_id) if is_admin else None,
    )


@router.put("/credentials/{org_id}", response_model=HelloAssoStatus)
def set_helloasso_credentials(
    org_id: str,
    credentials: HelloAssoCredentials,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Store or update HelloAsso API credentials. Secret is Fernet-encrypted, never returned."""
    _require_org_admin(UUID(org_id), current_user, session)

    if not ha_service.validate_credentials(
        credentials.api_client_id, credentials.api_client_secret
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid HelloAsso credentials — could not obtain an access token",
        )

    org_ha = session.exec(
        select(OrganizationHelloAsso).where(
            OrganizationHelloAsso.organization_id == UUID(org_id)
        )
    ).first()

    encrypted_secret = ha_service.encrypt(credentials.api_client_secret)

    if org_ha:
        org_ha.helloasso_slug = credentials.helloasso_slug
        org_ha.api_client_id = credentials.api_client_id
        org_ha.api_client_secret = encrypted_secret
        org_ha.cached_access_token = None
        org_ha.token_expires_at = None
    else:
        org_ha = OrganizationHelloAsso(
            organization_id=UUID(org_id),
            helloasso_slug=credentials.helloasso_slug,
            api_client_id=credentials.api_client_id,
            api_client_secret=encrypted_secret,
            connected_by_id=current_user.id,
        )

    session.add(org_ha)
    session.commit()
    session.refresh(org_ha)

    return HelloAssoStatus(
        connected=True,
        helloasso_slug=org_ha.helloasso_slug,
        api_client_id=org_ha.api_client_id,
    )


@router.delete("/credentials/{org_id}")
def delete_helloasso_credentials(
    org_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    _require_org_admin(UUID(org_id), current_user, session)

    org_ha = session.exec(
        select(OrganizationHelloAsso).where(
            OrganizationHelloAsso.organization_id == UUID(org_id)
        )
    ).first()
    if not org_ha:
        raise HTTPException(status_code=404, detail="No HelloAsso credentials found")

    session.delete(org_ha)
    session.commit()
    return {"message": "HelloAsso credentials removed"}


# ---------------------------------------------------------------------------
# Payment form lifecycle
# ---------------------------------------------------------------------------


@router.post("/events/{event_id}/payment-form", response_model=PaymentFormRead)
def create_payment_form(
    event_id: str,
    form_data: PaymentFormCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Propose a payment form for an event. No HelloAsso API call until approved."""
    event = session.get(Event, UUID(event_id))
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if not _can_propose_payment_form(event, current_user, session):
        raise HTTPException(
            status_code=403, detail="Not authorized to propose a payment form"
        )

    existing = session.exec(
        select(EventPaymentForm).where(EventPaymentForm.event_id == UUID(event_id))
    ).first()
    if existing:
        raise HTTPException(
            status_code=400, detail="A payment form already exists for this event"
        )

    if form_data.total_amount_cents <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    org = session.get(Organization, event.organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Event organization not found")

    form = EventPaymentForm(
        event_id=UUID(event_id),
        requesting_org_id=event.organization_id,
        approving_org_id=org.parent_id,
        total_amount_cents=form_data.total_amount_cents,
        item_name=form_data.item_name,
        options=(
            _json.dumps([o.model_dump() for o in form_data.options])
            if form_data.options
            else None
        ),
        created_by_id=current_user.id,
    )
    session.add(form)
    session.commit()
    session.refresh(form)

    background_tasks.add_task(_notify_parent_admins_of_pending_form, form.id, event.id)

    return _to_read(form, session)


@router.get("/events/{event_id}/payment-form", response_model=PaymentFormRead)
def get_payment_form(
    event_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    form = _get_form_or_404(event_id, session)
    return _to_read(form, session)


@router.put("/events/{event_id}/payment-form", response_model=PaymentFormRead)
def update_payment_form(
    event_id: str,
    update_data: PaymentFormUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Edit a payment form. Rejected forms cannot be edited.
    item_name / total_amount_cents can only be changed while PENDING.
    options and is_open can be changed at any time (including after approval).
    """
    form = _get_form_or_404(event_id, session)

    if form.status == PaymentFormStatus.REJECTED:
        raise HTTPException(
            status_code=400, detail="Cannot edit a rejected payment form"
        )

    if not _can_manage_form(form, current_user, session):
        raise HTTPException(status_code=403, detail="Not authorized")

    if update_data.is_open is not None:
        form.is_open = update_data.is_open

    if update_data.options is not None:
        form.options = _json.dumps([o.model_dump() for o in update_data.options])

    if form.status == PaymentFormStatus.PENDING:
        if update_data.item_name is not None:
            form.item_name = update_data.item_name
        if update_data.total_amount_cents is not None:
            if update_data.total_amount_cents <= 0:
                raise HTTPException(status_code=400, detail="Amount must be positive")
            form.total_amount_cents = update_data.total_amount_cents

    session.add(form)
    session.commit()
    session.refresh(form)

    return _to_read(form, session)


@router.delete("/events/{event_id}/payment-form")
def cancel_payment_form(
    event_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Cancel (delete) a PENDING payment form."""
    form = _get_form_or_404(event_id, session)

    if form.status != PaymentFormStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail="Only pending payment forms can be cancelled",
        )

    if not _can_manage_form(form, current_user, session):
        raise HTTPException(status_code=403, detail="Not authorized")

    session.delete(form)
    session.commit()
    return {"message": "Payment form cancelled"}


@router.post("/events/{event_id}/payment-form/approve", response_model=PaymentFormRead)
def approve_payment_form(
    event_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Approve a pending payment form. Checkout intents are created per-user on demand."""
    form = _get_form_or_404(event_id, session)

    if form.status != PaymentFormStatus.PENDING:
        raise HTTPException(
            status_code=400, detail="Only pending forms can be approved"
        )

    if not _can_review_payment_form(form, current_user, session):
        raise HTTPException(
            status_code=403, detail="Not authorized to approve payment forms"
        )

    approving_org_id = form.approving_org_id or form.requesting_org_id
    org_ha = session.exec(
        select(OrganizationHelloAsso).where(
            OrganizationHelloAsso.organization_id == approving_org_id
        )
    ).first()
    if not org_ha:
        raise HTTPException(
            status_code=400,
            detail="No HelloAsso account configured. Connect HelloAsso to the organization first.",
        )

    form.status = PaymentFormStatus.APPROVED
    form.reviewed_by_id = current_user.id
    form.reviewed_at = datetime.now(timezone.utc)
    form.rejection_message = None
    session.add(form)
    session.commit()
    session.refresh(form)

    event = session.get(Event, form.event_id)
    if event:
        background_tasks.add_task(_notify_creator, form.id, event.id, True)

    return _to_read(form, session)


@router.post("/events/{event_id}/payment-form/reject", response_model=PaymentFormRead)
def reject_payment_form(
    event_id: str,
    reject_data: PaymentFormReject,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    form = _get_form_or_404(event_id, session)

    if form.status != PaymentFormStatus.PENDING:
        raise HTTPException(
            status_code=400, detail="Only pending forms can be rejected"
        )

    if not _can_review_payment_form(form, current_user, session):
        raise HTTPException(
            status_code=403, detail="Not authorized to reject payment forms"
        )

    event = session.get(Event, form.event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    form.status = PaymentFormStatus.REJECTED
    form.rejection_message = reject_data.rejection_message
    form.reviewed_by_id = current_user.id
    form.reviewed_at = datetime.now(timezone.utc)
    session.add(form)
    session.commit()
    session.refresh(form)

    background_tasks.add_task(_notify_creator, form.id, event.id, False)

    return _to_read(form, session)


# ---------------------------------------------------------------------------
# On-demand checkout intent creation
# ---------------------------------------------------------------------------


@router.post(
    "/events/{event_id}/initiate-payment", response_model=PaymentInitiateResponse
)
def initiate_payment(
    event_id: str,
    request_data: PaymentInitiateRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Create a HelloAsso checkout intent for the current user with chosen options."""
    form = _get_form_or_404(event_id, session)

    if form.status != PaymentFormStatus.APPROVED:
        raise HTTPException(
            status_code=400,
            detail="Payment is not available — the form has not been approved yet",
        )

    if not form.is_open:
        raise HTTPException(
            status_code=400, detail="Payments are currently closed for this event"
        )

    options = _parse_options(form.options)
    for idx in request_data.selected_option_indices:
        if idx < 0 or idx >= len(options):
            raise HTTPException(status_code=400, detail=f"Invalid option index: {idx}")

    extra_cents = sum(
        options[i].price_cents for i in request_data.selected_option_indices
    )
    total_cents = form.total_amount_cents + extra_cents

    org_ha = None
    if form.approving_org_id:
        org_ha = session.exec(
            select(OrganizationHelloAsso).where(
                OrganizationHelloAsso.organization_id == form.approving_org_id
            )
        ).first()
    if not org_ha:
        org_ha = session.exec(
            select(OrganizationHelloAsso).where(
                OrganizationHelloAsso.organization_id == form.requesting_org_id
            )
        ).first()
    if not org_ha:
        raise HTTPException(
            status_code=503, detail="HelloAsso is not configured for this organization"
        )

    event = session.get(Event, form.event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    requesting_org = session.get(Organization, form.requesting_org_id)
    org_name = requesting_org.name if requesting_org else ""

    redirect_event_url = f"{_helloasso_redirect_base_url()}/events/{event.id}"

    if current_user.full_name and current_user.full_name.strip():
        name_parts = current_user.full_name.strip().split(" ", 1)
        payer_first = name_parts[0]
        payer_last = name_parts[1] if len(name_parts) > 1 else name_parts[0]
    else:
        # Derive a display name from the email local part (no @ or dots as names)
        local = (
            current_user.email.split("@")[0].replace(".", " ").replace("_", " ").strip()
        )
        name_parts = local.split(" ", 1)
        payer_first = name_parts[0].capitalize() or "Participant"
        payer_last = name_parts[1].capitalize() if len(name_parts) > 1 else payer_first

    # Build item name: org — event — item [+ options]
    item_parts = []
    if org_name:
        item_parts.append(org_name)
    item_parts.append(event.title)
    item_parts.append(form.item_name)
    item_name = " — ".join(item_parts)

    if request_data.selected_option_indices:
        option_names = [options[i].name for i in request_data.selected_option_indices]
        item_name = f"{item_name} + {', '.join(option_names)}"

    try:
        checkout_intent_id, redirect_url = ha_service.create_checkout_intent(
            org_ha=org_ha,
            session=session,
            amount_cents=total_cents,
            item_name=item_name,
            return_url=f"{redirect_event_url}?payment=success",
            back_url=redirect_event_url,
            error_url=f"{redirect_event_url}?payment=error",
            payer_email=current_user.email,
            payer_first_name=payer_first,
            payer_last_name=payer_last,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"HelloAsso API error: {exc}")

    entry = EventPaymentEntry(
        payment_form_id=form.id,
        user_id=current_user.id,
        checkout_intent_id=checkout_intent_id,
        selected_option_indices=_json.dumps(request_data.selected_option_indices),
        amount_cents=total_cents,
    )
    session.add(entry)

    form.last_checkout_intent_id = checkout_intent_id
    session.add(form)
    session.commit()

    return PaymentInitiateResponse(
        redirect_url=redirect_url,
        checkout_intent_id=checkout_intent_id,
    )


# ---------------------------------------------------------------------------
# Payment entries (per-user payment tracking)
# ---------------------------------------------------------------------------


@router.get(
    "/events/{event_id}/payment-form/entries", response_model=List[PaymentEntryRead]
)
def list_payment_entries(
    event_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """List individual payment entries. Requires org membership."""
    form = _get_form_or_404(event_id, session)

    if not (
        current_user.is_superadmin
        or _can_manage_form(form, current_user, session)
        or _can_review_payment_form(form, current_user, session)
    ):
        raise HTTPException(status_code=403, detail="Not authorized")

    entries = session.exec(
        select(EventPaymentEntry)
        .where(EventPaymentEntry.payment_form_id == form.id)
        .order_by(col(EventPaymentEntry.created_at).desc())
    ).all()

    result = []
    for entry in entries:
        user_obj = session.get(User, entry.user_id)
        indices: List[int] = []
        if entry.selected_option_indices:
            try:
                indices = _json.loads(entry.selected_option_indices)
            except Exception:
                pass
        result.append(
            PaymentEntryRead(
                id=entry.id,
                user_id=entry.user_id,
                user_name=user_obj.full_name or user_obj.email if user_obj else None,
                checkout_intent_id=entry.checkout_intent_id,
                amount_cents=entry.amount_cents,
                selected_option_indices=indices,
                completed=entry.completed,
                completed_at=entry.completed_at,
                created_at=entry.created_at,
            )
        )

    return result


# ---------------------------------------------------------------------------
# Pending forms list and dashboard
# ---------------------------------------------------------------------------


@router.get("/pending-forms/{org_id}", response_model=List[PaymentFormRead])
def list_pending_forms(
    org_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """List PENDING payment forms where this org is the approving org."""
    _require_org_admin(UUID(org_id), current_user, session)

    forms = session.exec(
        select(EventPaymentForm).where(
            EventPaymentForm.approving_org_id == UUID(org_id),
            EventPaymentForm.status == PaymentFormStatus.PENDING,
        )
    ).all()
    return [_to_read(f, session) for f in forms]


@router.get("/my-payment-forms", response_model=List[PaymentDashboardItem])
def my_payment_forms(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """All payment forms across orgs where the user has payment management rights."""
    if current_user.is_superadmin:
        forms = session.exec(select(EventPaymentForm)).all()
    else:
        memberships = session.exec(
            select(Membership).where(Membership.user_id == current_user.id)
        ).all()

        # Orgs where user can propose/manage
        proposing_org_ids = [
            m.organization_id
            for m in memberships
            if m.role == Role.ORG_ADMIN or m.can_manage_payment_forms
        ]
        # Orgs where user can approve (as parent org admin)
        approving_org_ids = [
            m.organization_id for m in memberships if m.role == Role.ORG_ADMIN
        ]

        if not proposing_org_ids and not approving_org_ids:
            return []

        seen: set = set()
        forms = []

        if proposing_org_ids:
            for f in session.exec(
                select(EventPaymentForm).where(
                    col(EventPaymentForm.requesting_org_id).in_(proposing_org_ids)
                )
            ).all():
                if f.id not in seen:
                    seen.add(f.id)
                    forms.append(f)

        if approving_org_ids:
            for f in session.exec(
                select(EventPaymentForm).where(
                    col(EventPaymentForm.approving_org_id).in_(approving_org_ids)  # type: ignore[union-attr]
                )
            ).all():
                if f.id not in seen:
                    seen.add(f.id)
                    forms.append(f)

    result = []
    for form in forms:
        event = session.get(Event, form.event_id)
        if not event:
            continue
        org = session.get(Organization, form.requesting_org_id)

        entries = session.exec(
            select(EventPaymentEntry).where(
                EventPaymentEntry.payment_form_id == form.id
            )
        ).all()

        result.append(
            PaymentDashboardItem(
                id=form.id,
                event_id=form.event_id,
                event_title=event.title,
                event_start_time=(
                    event.start_time.replace(tzinfo=timezone.utc)
                    if event.start_time.tzinfo is None
                    else event.start_time
                ),
                org_id=form.requesting_org_id,
                org_name=org.name if org else "Inconnue",
                item_name=form.item_name,
                total_amount_cents=form.total_amount_cents,
                options=_parse_options(form.options),
                status=form.status,
                is_open=form.is_open,
                entry_count=len(entries),
                completed_count=sum(1 for e in entries if e.completed),
                created_at=form.created_at,
            )
        )

    result.sort(key=lambda x: x.event_start_time, reverse=True)
    return result


# ---------------------------------------------------------------------------
# User's own payment history
# ---------------------------------------------------------------------------


def _build_my_entry(
    entry: EventPaymentEntry, session: Session
) -> Optional[MyPaymentEntryRead]:
    form = session.get(EventPaymentForm, entry.payment_form_id)
    if not form:
        return None
    event = session.get(Event, form.event_id)
    if not event:
        return None
    org = session.get(Organization, form.requesting_org_id)

    all_options = _parse_options(form.options)
    indices: List[int] = []
    if entry.selected_option_indices:
        try:
            indices = _json.loads(entry.selected_option_indices)
        except Exception:
            pass
    selected_options = [all_options[i] for i in indices if i < len(all_options)]

    start = event.start_time
    if start and start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)

    return MyPaymentEntryRead(
        id=entry.id,
        event_id=event.id,
        event_title=event.title,
        event_start_time=start or datetime.now(timezone.utc),
        org_name=org.name if org else "Inconnue",
        item_name=form.item_name,
        amount_cents=entry.amount_cents,
        payment_type=entry.payment_type,
        selected_options=selected_options,
        completed=entry.completed,
        created_at=entry.created_at,
    )


@router.get("/my-entries", response_model=List[MyPaymentEntryRead])
def my_payment_entries(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """All payment entries created by the current user."""
    entries = session.exec(
        select(EventPaymentEntry)
        .where(EventPaymentEntry.user_id == current_user.id)
        .order_by(col(EventPaymentEntry.created_at).desc())
    ).all()

    return [r for r in (_build_my_entry(e, session) for e in entries) if r is not None]


@router.get("/events/{event_id}/my-entry", response_model=Optional[MyPaymentEntryRead])
def my_event_entry(
    event_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Return the current user's most recent payment entry for this event, or null."""
    form = session.exec(
        select(EventPaymentForm).where(EventPaymentForm.event_id == UUID(event_id))
    ).first()
    if not form:
        return None

    entry = session.exec(
        select(EventPaymentEntry)
        .where(
            EventPaymentEntry.payment_form_id == form.id,
            EventPaymentEntry.user_id == current_user.id,
        )
        .order_by(col(EventPaymentEntry.created_at).desc())
    ).first()

    if not entry:
        return None
    return _build_my_entry(entry, session)


# ---------------------------------------------------------------------------
# Ticket validation (entrance control)
# ---------------------------------------------------------------------------


def _to_validation_entry(
    entry: EventPaymentEntry, form: EventPaymentForm, session: Session
) -> ValidationEntryRead:
    user_obj = session.get(User, entry.user_id) if entry.user_id else None
    all_options = _parse_options(form.options)
    indices: List[int] = []
    if entry.selected_option_indices:
        try:
            indices = _json.loads(entry.selected_option_indices)
        except Exception:
            pass
    selected_options = [all_options[i] for i in indices if i < len(all_options)]

    user_name = user_obj.full_name or user_obj.email if user_obj else None
    user_email = user_obj.email if user_obj else None
    display_name = user_name or entry.attendee_name or "Inconnu"

    return ValidationEntryRead(
        id=entry.id,
        user_name=user_name,
        user_email=user_email,
        attendee_name=entry.attendee_name,
        display_name=display_name,
        item_name=form.item_name,
        amount_cents=entry.amount_cents,
        payment_type=entry.payment_type,
        selected_options=selected_options,
        completed=entry.completed,
        validated=entry.validated,
        validated_at=entry.validated_at,
        created_at=entry.created_at,
    )


@router.get(
    "/events/{event_id}/validation-entries", response_model=List[ValidationEntryRead]
)
def get_validation_entries(
    event_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """All entries for a payment form. Requires org admin or can_manage_payment_forms."""
    form = _get_form_or_404(event_id, session)
    if not (
        current_user.is_superadmin
        or _can_manage_form(form, current_user, session)
        or _can_review_payment_form(form, current_user, session)
    ):
        raise HTTPException(status_code=403, detail="Not authorized")

    entries = session.exec(
        select(EventPaymentEntry)
        .where(EventPaymentEntry.payment_form_id == form.id)
        .order_by(col(EventPaymentEntry.created_at).desc())
    ).all()
    return [_to_validation_entry(e, form, session) for e in entries]


@router.post("/entries/{entry_id}/validate", response_model=ValidationEntryRead)
def validate_entry(
    entry_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Toggle validated state on a payment entry."""
    entry = session.get(EventPaymentEntry, UUID(entry_id))
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    form = session.get(EventPaymentForm, entry.payment_form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    if not (
        current_user.is_superadmin
        or _can_manage_form(form, current_user, session)
        or _can_review_payment_form(form, current_user, session)
    ):
        raise HTTPException(status_code=403, detail="Not authorized")

    entry.validated = not entry.validated
    entry.validated_at = datetime.now(timezone.utc) if entry.validated else None
    entry.validated_by_id = current_user.id if entry.validated else None
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return _to_validation_entry(entry, form, session)


def _normalize(s: str) -> str:
    """Fold accents and lowercase for fuzzy comparison."""
    return unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode().lower()


def _levenshtein(a: str, b: str) -> int:
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        curr = [i]
        for j, cb in enumerate(b, 1):
            curr.append(min(prev[j] + 1, curr[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = curr
    return prev[-1]


def _fuzzy_match(query: str, candidate: str, max_errors: int = 2) -> bool:
    """Return True if every query word matches some part of candidate.

    A word matches if it is a prefix/substring of a candidate word (handles
    partial typing like "Ale" → "Alexis") or within max_errors Levenshtein
    distance (handles typos like "Dupond" → "Dupont").
    """
    q_words = _normalize(query).split()
    c_words = _normalize(candidate).split()
    for qw in q_words:
        if not any(
            cw.startswith(qw) or qw in cw or _levenshtein(qw, cw) <= max_errors
            for cw in c_words
        ):
            return False
    return True


@router.get(
    "/events/{event_id}/attendee-search", response_model=List[AttendeeSearchResult]
)
def attendee_search(
    event_id: str,
    q: str = "",
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Search registered users and LDAP directory for manual entry autocomplete."""
    form = _get_form_or_404(event_id, session)
    if not (
        current_user.is_superadmin
        or _can_manage_form(form, current_user, session)
        or _can_review_payment_form(form, current_user, session)
    ):
        raise HTTPException(status_code=403, detail="Not authorized")

    q = q.strip()
    results: List[AttendeeSearchResult] = []
    seen_emails: set[str] = set()

    if q:
        pattern = f"%{q}%"

        # 1. Registered users (ilike for speed, then fuzzy re-rank client-side)
        users = session.exec(
            select(User)
            .where(
                or_(
                    col(User.full_name).ilike(pattern),
                    col(User.email).ilike(pattern),
                )
            )
            .limit(20)
        ).all()
        for u in users:
            if _fuzzy_match(q, (u.full_name or "") + " " + (u.email or "")):
                results.append(
                    AttendeeSearchResult(
                        id=u.id,
                        full_name=u.full_name,
                        email=u.email,
                        source="user",
                    )
                )
                if u.email:
                    seen_emails.add(u.email.lower())

        # 2. LDAP cache — skip already-found emails
        ldap_users = session.exec(
            select(LDAPUser)
            .where(
                or_(
                    col(LDAPUser.full_name).ilike(pattern),
                    col(LDAPUser.email).ilike(pattern),
                    col(LDAPUser.uid).ilike(pattern),
                )
            )
            .limit(20)
        ).all()
        for lu in ldap_users:
            if lu.email and lu.email.lower() in seen_emails:
                continue
            if _fuzzy_match(
                q, (lu.full_name or "") + " " + (lu.email or "") + " " + (lu.uid or "")
            ):
                results.append(
                    AttendeeSearchResult(
                        id=None,
                        full_name=lu.full_name,
                        email=lu.email,
                        uid=lu.uid,
                        source="ldap",
                    )
                )

    return results[:15]


@router.post(
    "/events/{event_id}/attendee-bulk-resolve", response_model=List[BulkResolveResult]
)
def attendee_bulk_resolve(
    event_id: str,
    request: BulkResolveRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Resolve a list of names/emails to User IDs, creating accounts from LDAP if needed."""
    form = _get_form_or_404(event_id, session)
    if not (
        current_user.is_superadmin
        or _can_manage_form(form, current_user, session)
        or _can_review_payment_form(form, current_user, session)
    ):
        raise HTTPException(status_code=403, detail="Not authorized")

    results: List[BulkResolveResult] = []

    for q in request.queries:
        q_clean = q.strip()
        if not q_clean:
            continue
            
        # Try finding a direct user match first
        users = session.exec(select(User)).all()
        best_user = None
        for u in users:
            if _fuzzy_match(q_clean, (u.full_name or "") + " " + (u.email or "")):
                best_user = u
                break
                
        if best_user:
            results.append(BulkResolveResult(query=q, user_id=str(best_user.id), full_name=best_user.full_name))
            continue
            
        # If not found, try LDAP
        ldap_users = session.exec(select(LDAPUser)).all()
        best_ldap = None
        for lu in ldap_users:
            if _fuzzy_match(q_clean, (lu.full_name or "") + " " + (lu.email or "") + " " + (lu.uid or "")):
                best_ldap = lu
                break
                
        if best_ldap and best_ldap.email:
            # Create user from LDAP
            new_user = User(
                email=best_ldap.email,
                full_name=best_ldap.full_name,
                is_active=True,
            )
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            results.append(BulkResolveResult(query=q, user_id=str(new_user.id), full_name=new_user.full_name))
        else:
            results.append(BulkResolveResult(query=q, user_id=None, full_name=None))

    return results

@router.post("/events/{event_id}/manual-entry", response_model=ValidationEntryRead)
def create_manual_entry(
    event_id: str,
    data: ManualEntryCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Add a manual payment entry (cash, cheque, etc.) without a HelloAsso checkout."""
    form = _get_form_or_404(event_id, session)
    if not (
        current_user.is_superadmin
        or _can_manage_form(form, current_user, session)
        or _can_review_payment_form(form, current_user, session)
    ):
        raise HTTPException(status_code=403, detail="Not authorized")

    # Compute amount
    options = _parse_options(form.options)
    base = form.total_amount_cents
    extra = sum(
        options[i].price_cents for i in data.selected_option_indices if i < len(options)
    )
    total = data.amount_cents if data.amount_cents is not None else base + extra

    entry = EventPaymentEntry(
        payment_form_id=form.id,
        user_id=None,
        checkout_intent_id=None,
        attendee_name=data.attendee_name,
        payment_type=data.payment_type.value,
        selected_option_indices=_json.dumps(data.selected_option_indices),
        amount_cents=total,
        completed=True,  # manual entries are considered paid
        completed_at=datetime.now(timezone.utc),
    )
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return _to_validation_entry(entry, form, session)


# ---------------------------------------------------------------------------
# Webhook (registered separately at /webhooks prefix in main.py)
# ---------------------------------------------------------------------------


@webhooks_router.post("/helloasso/{org_id}/{secret}")
async def helloasso_webhook(
    org_id: str,
    secret: str,
    request: Request,
    session: Session = Depends(get_session),
):
    """Receive HelloAsso payment notifications for a specific organization.

    The URL embeds an org-specific secret (HMAC-SHA256 of SECRET_KEY + org_id)
    so no additional signature header is needed.
    """
    # Verify the path-embedded secret
    expected_secret = _webhook_secret(org_id)
    if not hmac.compare_digest(secret, expected_secret):
        raise HTTPException(status_code=403, detail="Invalid webhook secret")

    body = await request.body()
    logger.info("[webhook] org=%s headers: %s", org_id, dict(request.headers))
    logger.info("[webhook] org=%s body: %s", org_id, body.decode(errors="replace"))

    try:
        data = _json.loads(body)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    event_type = data.get("eventType")
    payload = data.get("data", {})
    entry = None

    # Restrict to entries belonging to this org's payment forms
    org_form_ids = session.exec(
        select(EventPaymentForm.id).where(
            or_(
                EventPaymentForm.requesting_org_id == UUID(org_id),
                EventPaymentForm.approving_org_id == UUID(org_id),
            )
        )
    ).all()

    if event_type == "Order":
        # Order events contain checkoutIntentId — direct match
        checkout_intent_id = str(payload.get("checkoutIntentId", ""))
        if not checkout_intent_id:
            return {"message": "Order event missing checkoutIntentId, ignoring"}
        entry = session.exec(
            select(EventPaymentEntry).where(
                EventPaymentEntry.checkout_intent_id == checkout_intent_id,
                col(EventPaymentEntry.payment_form_id).in_(org_form_ids),
            )
        ).first()
        logger.info(
            "[webhook] Order event checkoutIntentId=%s entry=%s",
            checkout_intent_id,
            entry,
        )

    elif event_type == "Payment":
        # Payment events don't include checkoutIntentId; match by payer email + amount
        if payload.get("state") != "Authorized":
            logger.info("[webhook] Payment state=%s, ignoring", payload.get("state"))
            return {"message": "Payment not authorized, ignoring"}

        payer_email = payload.get("payer", {}).get("email", "")
        amount_cents = payload.get("amount", 0)

        user_obj = session.exec(select(User).where(User.email == payer_email)).first()
        if not user_obj:
            logger.warning("[webhook] no user for email=%s", payer_email)
            return {"message": "User not found, ignoring"}

        entry = session.exec(
            select(EventPaymentEntry)
            .where(
                EventPaymentEntry.user_id == user_obj.id,
                EventPaymentEntry.completed == False,
                EventPaymentEntry.amount_cents == amount_cents,
                col(EventPaymentEntry.payment_form_id).in_(org_form_ids),
            )
            .order_by(col(EventPaymentEntry.created_at).desc())
        ).first()
        logger.info(
            "[webhook] Payment event email=%s amount=%d entry=%s",
            payer_email,
            amount_cents,
            entry,
        )

    else:
        logger.info("[webhook] unknown eventType=%s, ignoring", event_type)
        return {"message": f"Unhandled event type {event_type}, ignoring"}

    if not entry:
        logger.warning("[webhook] no matching entry found")
        return {"message": "No matching entry, ignoring"}

    if entry.completed:
        logger.info("[webhook] entry %s already completed, skipping", entry.id)
        return {"message": "Already completed"}

    logger.info("[webhook] marking entry %s as completed", entry.id)
    _mark_entry_completed(entry, session)
    return {"message": "ok"}


def _mark_entry_completed(entry: EventPaymentEntry, session: Session) -> None:
    """Mark a payment entry and its form as completed."""
    entry.completed = True
    entry.completed_at = datetime.now(timezone.utc)
    session.add(entry)

    form = session.get(EventPaymentForm, entry.payment_form_id)
    if form:
        form.last_checkout_intent_id = entry.checkout_intent_id
        session.add(form)

    session.commit()


@router.post("/events/{event_id}/confirm-payment")
def confirm_payment(
    event_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Called by the frontend when the user returns from HelloAsso (returnUrl).

    Queries HelloAsso to verify the checkout intent is paid and marks the entry complete.
    """
    form = _get_form_or_404(event_id, session)

    # Find this user's most recent entry for this form (completed or not)
    entry = session.exec(
        select(EventPaymentEntry)
        .where(
            EventPaymentEntry.payment_form_id == form.id,
            EventPaymentEntry.user_id == current_user.id,
        )
        .order_by(col(EventPaymentEntry.created_at).desc())
    ).first()

    if not entry:
        raise HTTPException(status_code=404, detail="No payment entry found")

    # Webhook may have already marked it complete — return immediately
    if entry.completed:
        return {"completed": True}

    # Look up HelloAsso credentials: try approving org first, then requesting org
    org_ha = None
    for org_id in filter(None, [form.approving_org_id, form.requesting_org_id]):
        org_ha = session.exec(
            select(OrganizationHelloAsso).where(
                OrganizationHelloAsso.organization_id == org_id
            )
        ).first()
        if org_ha:
            break

    if not org_ha:
        raise HTTPException(status_code=503, detail="HelloAsso not configured")

    # Verify with HelloAsso API
    import httpx as _httpx

    token = ha_service.get_access_token(org_ha, session)
    url = ha_service._api_url(
        f"organizations/{org_ha.helloasso_slug}/checkout-intents/{entry.checkout_intent_id}"
    )
    logger.info("[confirm-payment] GET %s", url)
    resp = _httpx.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=15)
    logger.info(
        "[confirm-payment] response status=%s body=%s", resp.status_code, resp.text
    )

    if not resp.is_success:
        raise HTTPException(
            status_code=502, detail="Could not verify payment with HelloAsso"
        )

    intent_data = resp.json()
    order = intent_data.get("order")
    if not order:
        return {"completed": False, "message": "Payment not yet confirmed by HelloAsso"}

    _mark_entry_completed(entry, session)
    return {"completed": True}
