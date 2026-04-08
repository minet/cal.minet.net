from typing import List
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlmodel import Session, select

from app.api.auth import get_current_user, get_current_user_optional
from app.api.organizations import can_edit_organization
from app.database import get_session
from app.models import Membership, Organization, OrganizationImage, Role, StoredFile, User
from app.schemas import OrganizationImageRead
from app.services.storage import delete_file, upload_file

router = APIRouter()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _check_can_edit(org_id: str, current_user: User, session: Session):
    can_edit, reason = can_edit_organization(org_id, current_user, session)
    if not can_edit:
        raise HTTPException(status_code=403, detail="Non autorisé")


@router.get("/organizations/{org_id}/images", response_model=List[OrganizationImageRead])
def list_organization_images(
    org_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """List images for an organization. Only accessible to members (editor or above)."""
    org = session.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organisation introuvable")

    # Allow superadmin or any org member (viewer+) to list images
    if not current_user.is_superadmin:
        membership = session.exec(
            select(Membership).where(
                Membership.user_id == current_user.id,
                Membership.organization_id == org_id,
            )
        ).first()
        if not membership:
            raise HTTPException(status_code=403, detail="Non autorisé")

    images = session.exec(
        select(OrganizationImage).where(OrganizationImage.organization_id == org_id)
    ).all()
    return [OrganizationImageRead.from_model(img, session) for img in images]


@router.post("/organizations/{org_id}/images", response_model=OrganizationImageRead)
async def upload_organization_image(
    org_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Upload an image for an organization. Only org_admin or superadmin."""
    org = session.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organisation introuvable")

    _check_can_edit(org_id, current_user, session)

    if not file.filename or not allowed_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"Type de fichier non autorisé. Types acceptés : {', '.join(ALLOWED_EXTENSIONS)}",
        )
    if not file.content_type:
        raise HTTPException(status_code=400, detail="Type de contenu manquant")

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Fichier trop volumineux. Maximum : {MAX_FILE_SIZE // (1024 * 1024)}MB",
        )

    try:
        url = upload_file(contents, file.filename, file.content_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Échec de l'upload : {str(e)}")

    # Create a StoredFile record
    stored_filename = url.replace("/uploads/", "")
    sf = StoredFile(
        stored_filename=stored_filename,
        original_filename=file.filename,
        url=url,
        content_type=file.content_type,
        size=len(contents),
        uploaded_by_id=current_user.id,
        file_type="image",
        processed=False,
    )
    session.add(sf)
    session.flush()  # get sf.id

    image = OrganizationImage(
        id=uuid4(),
        organization_id=org_id,  # type: ignore
        filename=file.filename,
        stored_file_id=sf.id,
    )
    session.add(image)
    session.commit()
    session.refresh(image)
    return OrganizationImageRead.from_model(image, session)


@router.delete("/organizations/{org_id}/images/{image_id}")
def delete_organization_image(
    org_id: str,
    image_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Delete an image from an organization. Only org_admin or superadmin."""
    _check_can_edit(org_id, current_user, session)

    image = session.get(OrganizationImage, image_id)
    if not image or str(image.organization_id) != org_id:
        raise HTTPException(status_code=404, detail="Image introuvable")

    # Remove from MinIO via StoredFile
    if image.stored_file_id:
        sf = session.get(StoredFile, image.stored_file_id)
        if sf:
            delete_file(sf.url.replace("/uploads/", ""))

    session.delete(image)
    session.commit()
    return {"message": "Image supprimée"}
