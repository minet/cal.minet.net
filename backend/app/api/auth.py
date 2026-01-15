from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer
from app.models import User, Event, EventVisibility, Membership, Role
from sqlmodel import Session, select
from app.database import get_session
from app.models import User
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="auth/token", auto_error=False)

SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_THIS_SECRET_KEY")  # Use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30  # 30 days

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = session.exec(select(User).where(User.email == email)).first()
    if user is None or not user.is_active:
        raise credentials_exception
    return user

async def get_current_user_optional(token: Optional[str] = Depends(oauth2_scheme_optional), session: Session = Depends(get_session)):
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
    except JWTError:
        return None
    
    user = session.exec(select(User).where(User.email == email)).first()
    if user and not user.is_active:
        return None
    return user



# ... imports ...

@router.get("/me")
async def read_users_me(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get current user information with additional stats"""
    user_dict = current_user.model_dump()
    
    # Calculate pending approvals (Superadmin only)
    pending_count = 0
    if current_user.is_superadmin:
        pending_count = session.exec(
            select(Event).where(Event.visibility == EventVisibility.PUBLIC_PENDING)
        ).all()
        pending_count = len(pending_count)
    
    # Calculate rejected events (My events)
    # Events created by user
    user_rejected = session.exec(
        select(Event).where(
            Event.visibility == EventVisibility.PUBLIC_REJECTED,
            Event.created_by_id == current_user.id
        )
    ).all()
    rejected_ids = {e.id for e in user_rejected}
    
    # Events in orgs where user is admin
    admin_memberships = session.exec(
        select(Membership).where(
            Membership.user_id == current_user.id,
            Membership.role == Role.ORG_ADMIN
        )
    ).all()
    org_ids = [m.organization_id for m in admin_memberships]
    
    if org_ids:
        org_rejected = session.exec(
            select(Event).where(
                Event.visibility == EventVisibility.PUBLIC_REJECTED,
                Event.organization_id.in_(org_ids)
            )
        ).all()
        for e in org_rejected:
            rejected_ids.add(e.id)
            
    user_dict["pending_approvals_count"] = pending_count
    user_dict["rejected_events_count"] = len(rejected_ids)
    return user_dict

@router.put("/me")
async def update_user_profile(
    facebook_link: Optional[str] = None,
    phone_number: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update current user profile"""
    if facebook_link is not None:
        current_user.facebook_link = facebook_link
    if phone_number is not None:
        current_user.phone_number = phone_number
    
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    
    return current_user
