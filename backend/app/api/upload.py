import os
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlmodel import Session, select

from app.api.auth import get_current_user
from app.database import get_session
from app.models import Membership, Role, StoredFile, User
from app.services.storage import content_type_for, delete_file, upload_file

router = APIRouter()

# Allowed image extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Allowed video extensions
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'webm', 'mov', 'avi', 'mkv'}
MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100MB

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_video(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_VIDEO_EXTENSIONS

def check_can_upload(user: User, session: Session) -> None:
    """Raise 403 if the user cannot create or edit events (not a member of any org)."""
    if user.is_superadmin:
        return
    membership = session.exec(
        select(Membership).where(
            Membership.user_id == user.id,
            Membership.role.in_([Role.ORG_ADMIN, Role.ORG_MEMBER])  # pyright: ignore
        )
    ).first()
    if not membership:
        raise HTTPException(
            status_code=403,
            detail="You must be a member of at least one organisation to upload files"
        )

def can_delete_file(record: StoredFile, user: User, session: Session) -> bool:
    """Uploader, superadmin, or an editor (admin/member) of an organization the
    uploader belongs to."""
    if user.is_superadmin or record.uploaded_by_id == user.id:
        return True
    uploader_org_ids = select(Membership.organization_id).where(
        Membership.user_id == record.uploaded_by_id
    )
    shared_editor_membership = session.exec(
        select(Membership).where(
            Membership.user_id == user.id,
            Membership.role.in_([Role.ORG_ADMIN, Role.ORG_MEMBER]),  # pyright: ignore
            Membership.organization_id.in_(uploader_org_ids),  # pyright: ignore
        )
    ).first()
    return shared_editor_membership is not None

def record_upload(session: Session, url: str, original_filename: str, content_type: str, size: int, user: User) -> StoredFile:
    """Save a StoredFile record and return it."""
    stored_filename = url.removeprefix("/uploads/")
    file_type = "video" if content_type.startswith("video/") else "image"
    record = StoredFile(
        stored_filename=stored_filename,
        original_filename=original_filename,
        url=url,
        content_type=content_type,
        size=size,
        uploaded_by_id=user.id,
        file_type=file_type,
        processed=False,
    )
    session.add(record)
    session.commit()
    return record

@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Upload an image file. User must be able to create/edit events."""
    check_can_upload(current_user, session)

    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    if not allowed_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    contents = await file.read()

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
        )

    content_type = content_type_for(file.filename)
    try:
        url = upload_file(contents, file.filename, content_type)
        sf = record_upload(session, url, file.filename, content_type, len(contents), current_user)
        return {"url": url, "filename": file.filename, "stored_file_id": str(sf.id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.post("/video")
async def upload_video(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Upload a video file. User must be able to create/edit events."""
    check_can_upload(current_user, session)

    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    if not allowed_video(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_VIDEO_EXTENSIONS)}"
        )

    contents = await file.read()

    if len(contents) > MAX_VIDEO_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_VIDEO_SIZE // (1024*1024)}MB"
        )

    content_type = content_type_for(file.filename)
    try:
        url = upload_file(contents, file.filename, content_type)
        sf = record_upload(session, url, file.filename, content_type, len(contents), current_user)
        return {"url": url, "filename": file.filename, "stored_file_id": str(sf.id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.delete("/image")
async def delete_image(
    filename: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete an uploaded file (uploader, editors of the uploader's organizations,
    or superadmin).

    Removes it from storage and the tracking table.
    """
    # Normalize to stored_filename (strip /uploads/ prefix)
    stored_filename = filename.removeprefix("/uploads/")

    record = session.exec(
        select(StoredFile).where(StoredFile.stored_filename == stored_filename)
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="File not found")
    if not can_delete_file(record, current_user, session):
        raise HTTPException(status_code=403, detail="Not authorized to delete this file")

    session.delete(record)
    session.commit()

    success = delete_file(stored_filename)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete file")

    return {"message": "File deleted successfully"}
