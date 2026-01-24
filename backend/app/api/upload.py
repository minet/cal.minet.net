from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.api.auth import get_current_user
from app.models import User
from app.services.storage import upload_file, delete_file
import os

router = APIRouter()

# Allowed image extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload an image file
    Requires authentication
    """
    # Check file extension
    if not allowed_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Read file content
    contents = await file.read()
    
    # Check file size
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    # Upload to MinIO
    try:
        url = upload_file(contents, file.filename, file.content_type)
        return {"url": url, "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.delete("/image")
async def delete_image(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete an image file
    Requires authentication
    """
    # Remove /uploads/ prefix if present
    if filename.startswith('/uploads/'):
        filename = filename[9:]
    
    success = delete_file(filename)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete file")
    
    return {"message": "File deleted successfully"}
