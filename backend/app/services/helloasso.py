"""HelloAsso API service.

Each organization stores its own HelloAsso client_id + client_secret (API key pair).
Access tokens are obtained via OAuth2 client_credentials grant and cached in the DB
to avoid redundant requests to HelloAsso.

Base URL is controlled by the HELLOASSO_BASE_URL environment variable so staging and
production can be switched without code changes.  Default: https://api.helloasso-sandbox.com
"""

import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Tuple

import httpx
from cryptography.fernet import Fernet
from sqlmodel import Session

log = logging.getLogger(__name__)

from app.models import OrganizationHelloAsso

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

def _base_url() -> str:
    return os.getenv("HELLOASSO_BASE_URL", "https://api.helloasso-sandbox.com").rstrip("/")


def _token_url() -> str:
    return f"{_base_url()}/oauth2/token"


def _api_url(path: str) -> str:
    return f"{_base_url()}/v5/{path.lstrip('/')}"


# ---------------------------------------------------------------------------
# Encryption helpers
# ---------------------------------------------------------------------------

def _get_fernet() -> Fernet:
    key = os.getenv("TOKEN_ENCRYPTION_KEY", "")
    if not key:
        raise RuntimeError(
            "TOKEN_ENCRYPTION_KEY environment variable is not set. "
            "Generate one with: "
            "python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
        )
    return Fernet(key.encode())


def encrypt(value: str) -> str:
    return _get_fernet().encrypt(value.encode()).decode()


def decrypt(value: str) -> str:
    return _get_fernet().decrypt(value.encode()).decode()


# ---------------------------------------------------------------------------
# Token management
# ---------------------------------------------------------------------------

def get_access_token(org_ha: OrganizationHelloAsso, session: Session) -> str:
    """Return a valid access token for this org, refreshing via client_credentials if needed.

    The token is cached (encrypted) in the DB to minimise calls to HelloAsso.
    """
    now = datetime.now(timezone.utc)

    # Use cached token if still valid (with 60-second safety margin)
    if org_ha.cached_access_token and org_ha.token_expires_at:
        expires_at = (
            org_ha.token_expires_at
            if org_ha.token_expires_at.tzinfo
            else org_ha.token_expires_at.replace(tzinfo=timezone.utc)
        )
        if expires_at > now + timedelta(seconds=60):
            return decrypt(org_ha.cached_access_token)

    # Fetch a fresh token
    client_secret = decrypt(org_ha.api_client_secret)

    token_url = _token_url()
    log.info("[HelloAsso] POST %s  body=grant_type=client_credentials&client_id=%s&client_secret=***", token_url, org_ha.api_client_id)
    response = httpx.post(
        token_url,
        data={
            "grant_type": "client_credentials",
            "client_id": org_ha.api_client_id,
            "client_secret": client_secret,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=15,
    )
    log.info("[HelloAsso] token response  status=%s  body=%s", response.status_code, response.text)
    response.raise_for_status()
    token_data = response.json()

    access_token = token_data["access_token"]
    expires_in = token_data.get("expires_in", 1800)

    # Persist cached token
    org_ha.cached_access_token = encrypt(access_token)
    org_ha.token_expires_at = now + timedelta(seconds=expires_in)
    session.add(org_ha)
    session.commit()
    session.refresh(org_ha)

    return access_token


def validate_credentials(api_client_id: str, api_client_secret: str) -> bool:
    """Try to fetch a token with the given credentials and return True if successful."""
    try:
        response = httpx.post(
            _token_url(),
            data={
                "grant_type": "client_credentials",
                "client_id": api_client_id,
                "client_secret": api_client_secret,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10,
        )
        return response.status_code == 200
    except Exception:
        return False


# ---------------------------------------------------------------------------
# HelloAsso API calls
# ---------------------------------------------------------------------------

def create_checkout_intent(
    org_ha: OrganizationHelloAsso,
    session: Session,
    *,
    amount_cents: int,
    item_name: str,
    return_url: str,
    back_url: str,
    error_url: str,
    payer_email: str,
    payer_first_name: str,
    payer_last_name: str,
) -> Tuple[str, str]:
    """Create a HelloAsso checkout intent.

    Returns a tuple of (checkoutIntentId, redirectUrl).
    """
    token = get_access_token(org_ha, session)

    payload = {
        "totalAmount": amount_cents,
        "initialAmount": amount_cents,
        "itemName": item_name,
        "backUrl": back_url,
        "errorUrl": error_url,
        "returnUrl": return_url,
        "containsDonation": False,
        "payer": {
            "email": payer_email,
            "firstName": payer_first_name,
            "lastName": payer_last_name,
        },
    }

    url = _api_url(f"organizations/{org_ha.helloasso_slug}/checkout-intents")
    log.info("[HelloAsso] POST %s  payload=%s", url, payload)
    response = httpx.post(
        url,
        json=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        timeout=15,
    )
    log.info("[HelloAsso] checkout-intents response  status=%s  body=%s", response.status_code, response.text)
    if not response.is_success:
        raise RuntimeError(
            f"{response.status_code} from HelloAsso: {response.text}"
        )
    data = response.json()
    # The sandbox API returns "id" (int); production may return "checkoutIntentId"
    checkout_id = data.get("checkoutIntentId") or str(data["id"])
    return checkout_id, data["redirectUrl"]
