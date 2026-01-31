from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app.api.auth import get_current_user
from app.database import get_session
from app.models import Organization, Subscription, Tag, User

router = APIRouter()

class SubscriptionCreate(BaseModel):
    organization_id: str
    tag_id: str

@router.get("/me")
async def get_my_subscriptions(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get all subscriptions for the current user"""
    subscriptions = session.exec(
        select(Subscription).where(Subscription.user_id == current_user.id)
    ).all()
    
    # Check for subscribe_all
    subscribe_all = False
    for sub in subscriptions:
        if sub.subscribe_all:
            subscribe_all = True
            break
    
    result = {
        "subscribe_all": subscribe_all,
        "organizations": [],
        "tags": []
    }
    
    for sub in subscriptions:
        if sub.organization_id:
            org = session.get(Organization, sub.organization_id)
            if org:
                result["organizations"].append({
                    "id": str(sub.id),
                    "organization": {
                        "id": str(org.id),
                        "name": org.name,
                        "logo_url": org.logo_url
                    }
                })
        elif sub.tag_id:
            tag = session.get(Tag, sub.tag_id)
            if tag:
                # Fetch organization for the tag
                org = session.get(Organization, tag.organization_id)
                org_data = None
                if org:
                    org_data = {
                        "id": str(org.id),
                        "name": org.name,
                        "logo_url": org.logo_url
                    }

                result["tags"].append({
                    "id": str(sub.id),
                    "tag": {
                        "id": str(tag.id),
                        "name": tag.name,
                        "color": tag.color,
                        "organization": org_data
                    }
                })
    
    return result

@router.post("/organizations/{org_id}")
async def subscribe_to_organization(
    org_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Subscribe to an organization"""
    # Check if organization exists
    org = session.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Check if already subscribed
    existing = session.exec(
        select(Subscription).where(
            Subscription.user_id == current_user.id,
            Subscription.organization_id == org_id
        )
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Already subscribed")
    
    # Create subscription
    subscription = Subscription(
        user_id=current_user.id,
        organization_id=UUID(org_id)
    )
    session.add(subscription)
    session.commit()
    session.refresh(subscription)
    
    return {"message": "Subscribed successfully", "subscription_id": str(subscription.id)}

@router.delete("/organizations/{org_id}")
async def unsubscribe_from_organization(
    org_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Unsubscribe from an organization"""
    subscription = session.exec(
        select(Subscription).where(
            Subscription.user_id == current_user.id,
            Subscription.organization_id == org_id
        )
    ).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    session.delete(subscription)
    session.commit()
    
    return {"message": "Unsubscribed successfully"}

@router.post("/tags/{tag_id}")
async def subscribe_to_tag(
    tag_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Subscribe to a tag"""
    # Check if tag exists
    tag = session.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    # Check if already subscribed
    existing = session.exec(
        select(Subscription).where(
            Subscription.user_id == current_user.id,
            Subscription.tag_id == tag_id
        )
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Already subscribed")
    
    # Create subscription
    subscription = Subscription(
        user_id=current_user.id,
        tag_id=UUID(tag_id)
    )
    session.add(subscription)
    session.commit()
    session.refresh(subscription)
    
    return {"message": "Subscribed successfully", "subscription_id": str(subscription.id)}

@router.delete("/tags/{tag_id}")
async def unsubscribe_from_tag(
    tag_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Unsubscribe from a tag"""
    subscription = session.exec(
        select(Subscription).where(
            Subscription.user_id == current_user.id,
            Subscription.tag_id == tag_id
        )
    ).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    session.delete(subscription)
    session.commit()
    
    return {"message": "Unsubscribed successfully"}

@router.post("/all")
async def subscribe_to_all(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Subscribe to all events"""
    # Check if already subscribed to all
    existing = session.exec(
        select(Subscription).where(
            Subscription.user_id == current_user.id,
            Subscription.subscribe_all == True
        )
    ).first()
    
    if existing:
        return {"message": "Already subscribed to all"}
    
    # Create subscribe-all subscription
    subscription = Subscription(
        user_id=current_user.id,
        subscribe_all=True
    )
    session.add(subscription)
    session.commit()
    session.refresh(subscription)
    
    return {"message": "Subscribed to all successfully"}

@router.delete("/all")
async def unsubscribe_from_all(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Unsubscribe from all events"""
    subscription = session.exec(
        select(Subscription).where(
            Subscription.user_id == current_user.id,
            Subscription.subscribe_all == True
        )
    ).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Not subscribed to all")
    
    session.delete(subscription)
    session.commit()
    
    return {"message": "Unsubscribed from all successfully"}
