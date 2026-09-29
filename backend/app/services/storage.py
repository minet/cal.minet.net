import os
from pathlib import Path
import tempfile
from uuid import uuid4

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "/data/uploads"))


def _path_for(filename: str) -> Path:
    """Resolve a stored filename to its path, rejecting anything outside UPLOAD_DIR"""
    if not filename or Path(filename).name != filename:
        raise ValueError(f"Invalid stored filename: {filename!r}")
    return UPLOAD_DIR / filename


def _write_atomic(path: Path, data: bytes) -> None:
    """Write to a temp file then rename, so nginx never serves a partial file"""
    fd, tmp_path = tempfile.mkstemp(dir=path.parent, prefix=".tmp-")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        os.chmod(tmp_path, 0o644)
        os.replace(tmp_path, path)
    except BaseException:
        Path(tmp_path).unlink(missing_ok=True)
        raise


CONTENT_TYPES_BY_EXTENSION = {
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "gif": "image/gif",
    "webp": "image/webp",
    "svg": "image/svg+xml",
    "mp4": "video/mp4",
    "webm": "video/webm",
    "mov": "video/quicktime",
    "avi": "video/x-msvideo",
    "mkv": "video/x-matroska",
}


def content_type_for(filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return CONTENT_TYPES_BY_EXTENSION.get(ext, "application/octet-stream")


def upload_file(file_data: bytes, filename: str) -> str:
    """
    Store a file in the upload directory and return the public URL
    
    Args:
        file_data: The file content as bytes
        filename: Original filename
    
    Returns:
        Public URL of the uploaded file
    """
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    # Generate a unique filename
    ext = filename.rsplit('.', 1)[1] if '.' in filename else ''
    unique_filename = f"{uuid4()}.{ext}" if ext else str(uuid4())
    
    _write_atomic(_path_for(unique_filename), file_data)
    
    # Return the public URL (served by nginx)
    return f"/uploads/{unique_filename}"

def delete_file(filename: str) -> bool:
    """
    Delete a file from the upload directory
    
    Args:
        filename: The filename to delete (without /uploads/ prefix)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        _path_for(filename).unlink(missing_ok=True)
        return True
    except (OSError, ValueError) as e:
        print(f"Error deleting file: {e}")
        return False
