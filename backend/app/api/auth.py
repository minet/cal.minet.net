from datetime import datetime, timedelta, timezone
import os
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlmodel import Session, select, and_, func

from app.database import get_session
from app.models import Event, EventVisibility, Membership, Role, User
from app.models import User

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="auth/token", auto_error=False)

SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_THIS_SECRET_KEY")  # Use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24 * 30  # 30 days

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
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
        email: str | None = payload.get("sub")
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
        email: str | None = payload.get("sub")
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
            select(func.count(Event.id)).where(Event.visibility == EventVisibility.PUBLIC_PENDING) #pyright: ignore
        ).first()
        
    # Calculate rejected events (My events)
    # Events created by user
    user_rejected = session.exec(
        select(func.count(Event.id)) #pyright: ignore
        .distinct()
        .outerjoin(
            Membership,
            and_(
                Membership.organization_id == Event.organization_id,
                Membership.user_id == current_user.id,
                Membership.role.in_([Role.ORG_ADMIN, Role.ORG_MEMBER]) #pyright: ignore
            )
        )
        .where(
            Membership.id.is_not(None), #pyright: ignore
            Event.visibility == EventVisibility.PUBLIC_REJECTED,
            Event.start_time > datetime.now(timezone.utc)
        )
    ).first()
            
    user_dict["pending_approvals_count"] = pending_count
    user_dict["rejected_events_count"] = user_rejected
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
