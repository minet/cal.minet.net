import json
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, col, select

from app.api.auth import get_current_user
from app.database import get_session
from app.models import ChangelogAudience, ChangelogEntry, Membership, Role, User
from app.schemas import ChangelogEntryCreate, ChangelogEntryRead, ChangelogEntryUpdate

router = APIRouter()


def _entry_to_read(entry: ChangelogEntry) -> ChangelogEntryRead:
    image_urls = None
    if entry.image_urls:
        try:
            image_urls = json.loads(entry.image_urls)
        except Exception:
            image_urls = []
    return ChangelogEntryRead(
        id=entry.id,
        title=entry.title,
        content=entry.content,
        audience=entry.audience,
        image_urls=image_urls,
        created_at=entry.created_at,
    )


def _user_matches_audience(user: User, audience: ChangelogAudience, session: Session) -> bool:
    if audience == ChangelogAudience.ALL:
        return True
    memberships = session.exec(select(Membership).where(Membership.user_id == user.id)).all()
    if audience == ChangelogAudience.ORG_VIEWER_PLUS:
        return len(memberships) > 0
    if audience == ChangelogAudience.ORG_MEMBER_PLUS:
        return any(m.role in (Role.ORG_MEMBER, Role.ORG_ADMIN) for m in memberships)
    if audience == ChangelogAudience.ORG_ADMIN_PLUS:
        return any(m.role == Role.ORG_ADMIN for m in memberships)
    if audience == ChangelogAudience.TREASURY:
        return any(m.can_manage_payment_forms for m in memberships)
    return True


@router.get("", response_model=List[ChangelogEntryRead])
def list_changelogs(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> List[ChangelogEntryRead]:
    entries = session.exec(
        select(ChangelogEntry).order_by(col(ChangelogEntry.created_at).desc())
    ).all()
    return [
        _entry_to_read(e)
        for e in entries
        if _user_matches_audience(current_user, e.audience, session)
    ]


@router.get("/unseen", response_model=List[ChangelogEntryRead])
def list_unseen_changelogs(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> List[ChangelogEntryRead]:
    last_seen_at = None
    if current_user.last_seen_changelog_id:
        last_entry = session.get(ChangelogEntry, current_user.last_seen_changelog_id)
        if last_entry:
            last_seen_at = last_entry.created_at

    query = select(ChangelogEntry).order_by(col(ChangelogEntry.created_at).asc())
    if last_seen_at is not None:
        query = query.where(col(ChangelogEntry.created_at) > last_seen_at)

    entries = session.exec(query).all()
    return [
        _entry_to_read(e)
        for e in entries
        if _user_matches_audience(current_user, e.audience, session)
    ]


@router.post("", response_model=ChangelogEntryRead)
def create_changelog(
    data: ChangelogEntryCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ChangelogEntryRead:
    if not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Not authorized")
    entry = ChangelogEntry(
        title=data.title,
        content=data.content,
        audience=data.audience,
        image_urls=json.dumps(data.image_urls) if data.image_urls else None,
    )
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return _entry_to_read(entry)


@router.put("/{entry_id}", response_model=ChangelogEntryRead)
def update_changelog(
    entry_id: UUID,
    data: ChangelogEntryUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ChangelogEntryRead:
    if not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Not authorized")
    entry = session.get(ChangelogEntry, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Not found")
    if data.title is not None:
        entry.title = data.title
    if data.content is not None:
        entry.content = data.content
    if data.audience is not None:
        entry.audience = data.audience
    if data.image_urls is not None:
        entry.image_urls = json.dumps(data.image_urls)
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return _entry_to_read(entry)


@router.delete("/{entry_id}")
def delete_changelog(
    entry_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict:
    if not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Not authorized")
    entry = session.get(ChangelogEntry, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Not found")
    session.delete(entry)
    session.commit()
    return {"ok": True}


@router.post("/mark-seen/{entry_id}")
def mark_seen(
    entry_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict:
    entry = session.get(ChangelogEntry, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Not found")

    # Only advance, never regress
    if current_user.last_seen_changelog_id:
        current_last = session.get(ChangelogEntry, current_user.last_seen_changelog_id)
        if current_last and current_last.created_at >= entry.created_at:
            return {"ok": True}

    current_user.last_seen_changelog_id = entry_id
    session.add(current_user)
    session.commit()
    return {"ok": True}
