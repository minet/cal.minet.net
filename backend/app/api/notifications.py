from datetime import datetime, timedelta, timezone
import json
import logging
import os

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.api.auth import get_current_user
from app.database import get_session
from app.models import Event, EventVisibility, Subscription, User, UserPushToken
from app.schemas import Message, PushTokenCreate
from pywebpush import WebPushException, webpush

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/vapid-public-key")
def get_vapid_public_key():
    return {"public_key": os.getenv("VAPID_PUBLIC_KEY")}

@router.post("/subscribe", response_model=Message)
def subscribe_push(
    token_data: PushTokenCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    existing_token = session.exec(
        select(UserPushToken).where(
            UserPushToken.user_id == current_user.id,
            UserPushToken.endpoint == token_data.endpoint
        )
    ).first()
    
    if existing_token:
        if existing_token.keys != token_data.keys:
            existing_token.keys = token_data.keys
            session.add(existing_token)
            session.commit()
        return {"message": "Token updated"}
    
    new_token = UserPushToken(
        user_id=current_user.id,
        endpoint=token_data.endpoint,
        keys=token_data.keys
    )
    session.add(new_token)
    session.commit()
    
    return {"message": "Subscribed to push notifications"}

@router.delete("/unsubscribe", response_model=Message)
def unsubscribe_push(
    endpoint: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    token = session.exec(
        select(UserPushToken).where(
            UserPushToken.user_id == current_user.id,
            UserPushToken.endpoint == endpoint
        )
    ).first()
    
    if token:
        session.delete(token)
        session.commit()
        return {"message": "Unsubscribed"}
        
    return {"message": "Token not found"}

def _send_push_notification(subscription_info, message_body, vapid_private_key, vapid_claims):
    try:
        webpush(
            subscription_info=subscription_info,
            data=message_body,
            vapid_private_key=vapid_private_key,
            vapid_claims=vapid_claims
        )
    except WebPushException as ex:
        if ex.response and ex.response.status_code == 410:
            pass
        logger.error(f"WebPush Error: {ex}")
    except Exception as e:
        logger.error(f"Push Error: {e}")

def process_notifications(session: Session):
    cron_delay = int(os.getenv("CRON_DELAY", "900"))
    vapid_private_key = os.getenv("VAPID_PRIVATE_KEY")
    vapid_claims = {"sub": "mailto:" + os.getenv("ADMIN_EMAIL", "admin@example.com")}

    if not vapid_private_key:
        logger.warning("VAPID_PRIVATE_KEY not set")
        return 0

    now = datetime.now(timezone.utc)
    
    upcoming_events = session.exec(
        select(Event).where(
            Event.start_time > now,
            Event.start_time < now + timedelta(days=1),
            Event.visibility == EventVisibility.PUBLIC_APPROVED
        )
    ).all()
    
    sent_count = 0
    half_delay = cron_delay / 60 / 2

    for event in upcoming_events:
        event_start = event.start_time.replace(tzinfo=timezone.utc) if event.start_time.tzinfo is None else event.start_time
        minutes_until = (event_start - now).total_seconds() / 60
        
        lower_bound = minutes_until - half_delay
        upper_bound = minutes_until + half_delay
        
        potential_users = session.exec(
            select(User).join(UserPushToken).where(
                User.notification_delay >= lower_bound,
                User.notification_delay <= upper_bound
            ).distinct()
        ).all()
        
        for user in potential_users:
            is_subscribed = session.exec(
                select(Subscription).where(
                    Subscription.user_id == user.id,
                    (Subscription.organization_id == event.organization_id)
                )
            ).first()

            if not is_subscribed:
                for et in event.event_tags:
                    if session.exec(
                        select(Subscription).where(
                            Subscription.user_id == user.id,
                            Subscription.tag_id == et.tag_id
                        )
                    ).first():
                        is_subscribed = True
                        break
            
            if is_subscribed:
                payload = json.dumps({
                    "title": f"Rappel: {event.title}",
                    "body": f"L'événement commence dans {int(minutes_until)} minutes" + (f" à {event.location}." if event.location else "."),
                    "icon": "/CalendINT_icon.svg",
                    "data": { "url": f"/events/{event.id}" }
                })
                
                for token in user.push_tokens:
                    try:
                        _send_push_notification(
                            { "endpoint": token.endpoint, "keys": json.loads(token.keys) },
                            payload,
                            vapid_private_key,
                            vapid_claims
                        )
                        sent_count += 1
                    except Exception:
                        continue

    return sent_count

@router.get("/cron", response_model=Message)
def trigger_notifications_manual(
    key: str,
    session: Session = Depends(get_session)
):
    cron_key = os.getenv("CRON_KEY")
    if not cron_key or key != cron_key:
        raise HTTPException(status_code=403, detail="Invalid cron key")

    count = process_notifications(session)
    return {"message": f"Processed {count} notifications"}
