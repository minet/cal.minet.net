from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from typing import Optional
import os
from datetime import datetime, timedelta
from app.database import get_session
from app.models import User
from app.api.auth import create_access_token

router = APIRouter()

# Load environment variables
config = Config('.env')

# Configure OAuth
oauth = OAuth(config)

# CAMPUS OAuth (Generic OpenID Connect Provider)
oauth.register(
    name='campus',
    client_id=config('CAMPUS_CLIENT_ID', default=''),
    client_secret=config('CAMPUS_CLIENT_SECRET', default=''),
    #authorize_url=config('CAMPUS_AUTH_URL', default=''),
    server_metadata_url=config('CAMPUS_METADATA_URL', default=''),
    client_kwargs={'scope': 'openid email profile'}
)



def get_or_create_user(email: str, full_name: Optional[str], session: Session) -> User:
    """Get existing user or create new one from OIDC data"""
    # Check if user exists
    user = session.exec(select(User).where(User.email == email)).first()
    
    if user:
        # Update name if provided and different
        if full_name and user.full_name != full_name:
            user.full_name = full_name
            session.add(user)
            session.commit()
            session.refresh(user)
        return user
    
    # Create new user
    new_user = User(
        email=email,
        full_name=full_name or email,
        is_active=True,
        is_superadmin=False
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    return new_user

@router.get("/login/campus")
async def login_campus(request: Request):
    """Initiate CAMPUS OAuth flow"""
    redirect_uri = f"{config('APP_BASE_URL', default='http://localhost')}/api/auth/callback/campus"
    return await oauth.campus.authorize_redirect(request, redirect_uri)

@router.get("/callback/campus")
async def callback_campus(request: Request, session: Session = Depends(get_session)):
    """Handle CAMPUS OAuth callback"""
    try:
        token = await oauth.campus.authorize_access_token(request)
        user_info = token.get('userinfo')
        
        if not user_info or not user_info.get('email'):
            raise HTTPException(status_code=400, detail="Could not get user info from CAMPUS")
        
        # Get or create user
        user = get_or_create_user(
            email=user_info['email'],
            full_name=user_info.get('name'),
            session=session
        )
        
        # Create JWT token for our app
        access_token = create_access_token(data={"sub": user.email})
        
        # Redirect to frontend with token
        return RedirectResponse(
            url=f"{config('APP_BASE_URL', default='http://localhost')}/?token={access_token}",
            status_code=302
        )
        
    except Exception as e:
        print(f"CAMPUS OAuth error: {e}")
        return RedirectResponse(
            url=f"{config('APP_BASE_URL', default='http://localhost')}/login?error=oauth_failed",
            status_code=302
        )


