from datetime import datetime
import os
import ssl
from typing import List
from uuid import uuid4

from fastapi import APIRouter, Body, Depends, HTTPException
from ldap3 import ALL, Connection, SUBTREE, Server, Tls
from pydantic import BaseModel
from sqlmodel import Session, col, delete, select

from app.api.auth import get_current_user
from app.database import get_session
from app.models import LDAPUser, User
from app.schemas import UserRead

router = APIRouter()

class LDAPSyncRequest(BaseModel):
    username: str
    password: str

class LDAPUserRead(BaseModel):
    id: str
    email: str
    full_name: str | None
    uid: str | None

@router.post("/ldap/sync")
async def sync_ldap_users(
    creds: LDAPSyncRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Sync users from LDAP to local cache table (Superadmin only)"""
    if not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Superadmin access required")

    ldap_host = os.getenv("LDAP_HOST", "ldapha.imtbs-tsp.eu")
    ldap_port = int(os.getenv("LDAP_PORT", "636"))
    base_dn = os.getenv("LDAP_BASE_DN", "ou=active,dc=int-evry,dc=fr")
    ignore_certs = os.getenv("LDAP_IGNORE_CERTS", "true").lower() in ("true", "1", "yes", "y")
    
    # Construct User DN
    user_dn = f"uid={creds.username},{base_dn}"
    
    try:
        if ignore_certs:
            tls = Tls(
                validate=ssl.CERT_NONE,
                version=ssl.PROTOCOL_TLS_CLIENT,
                ciphers='ALL:@SECLEVEL=1'
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
            search_filter='(&(objectClass=person)(mail=*))',
            search_scope=SUBTREE,
            attributes=['mail', 'cn', 'displayName', 'uid', 'givenName', 'sn']
        )
        
        entries = conn.entries
        
        # Clear existing table
        # Note: SQLModel doesn't directly support `session.exec(delete(Model))` identically to select sometimes, 
        # but SQLAlchemy delete object works.
        stmt = delete(LDAPUser)
        session.exec(stmt) # pyright: ignore
        session.commit() 
        
        new_users = []
        for entry in entries:
            # ldap3 attributes are dynamically valid
            mail_val = entry.mail.value if hasattr(entry.mail, 'value') else str(entry.mail)
            if not mail_val:
                continue
                
            uid_val = None
            if hasattr(entry, 'uid') and entry.uid:
                uid_val = entry.uid.value if hasattr(entry.uid, 'value') else str(entry.uid)
            
            # Helper for name
            full_name = None
            if hasattr(entry, 'displayName') and entry.displayName:
                full_name = str(entry.displayName)
            elif hasattr(entry, 'cn') and entry.cn:
                full_name = str(entry.cn)
                
            ldap_user = LDAPUser(
                id=uuid4(),
                email=str(mail_val),
                full_name=full_name,
                uid=str(uid_val),
                synced_at=datetime.now()
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
    session: Session = Depends(get_session)
):
    """Search users in the LDAP cache"""
    if not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Superadmin access required")
        
    query = select(LDAPUser)
    if q:
        search_pattern = f"%{q}%"
        query = query.where(
            (col(LDAPUser.full_name).ilike(search_pattern)) | 
            (col(LDAPUser.email).ilike(search_pattern)) |
            (col(LDAPUser.uid).ilike(search_pattern))
        )
    
    query = query.limit(50)
    users = session.exec(query).all()
    
    return [
        LDAPUserRead(
            id=str(u.id),
            email=u.email,
            full_name=u.full_name,
            uid=u.uid
        ) for u in users
    ]

@router.post("/housekeeping")
async def housekeeping(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Trigger housekeeping to delete organizations that passed their delete_after date"""
    from datetime import datetime, timezone
    from app.models import Organization
    from app.api.organizations import delete_organization

    if not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Superadmin access required")

    now = datetime.now(timezone.utc)
    orgs_to_delete = session.exec(
        select(Organization).where(
            Organization.delete_after != None,
            col(Organization.delete_after) <= now
        )
    ).all()

    count = 0
    errors = 0
    for org in orgs_to_delete:
        try:
            delete_organization(str(org.id), current_user, session)
            count += 1
        except Exception as e:
            print(f"Error deleting org {org.id}: {e}")
            errors += 1

    return {"message": f"Housekeeping complete. Deleted {count} orgs. Errors: {errors}"}

@router.get("/ldap/orphans", response_model=List[UserRead])
async def get_ldap_orphaned_users(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Retrieve users absent from LDAP cache that are not exempt"""
    from app.models import GHOST_USER_ID, LDAPUser
    from sqlmodel import func

    if not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Superadmin access required")

    ldap_count = session.exec(select(func.count(col(LDAPUser.id)))).first()
    if not ldap_count:
        return []

    subq = select(LDAPUser.email)
    
    orphans = session.exec(
        select(User).where(
            User.email.notin_(subq), # pyright: ignore
            User.exempt_from_rgpd_delete == False,
            User.id != GHOST_USER_ID
        )
    ).all()
    
    return [u for u in orphans]
