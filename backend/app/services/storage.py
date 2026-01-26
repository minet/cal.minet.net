from minio import Minio
from minio.error import S3Error
import os
from io import BytesIO
from uuid import uuid4
import json

# MinIO client configuration
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "calendint")
MINIO_SECURE = os.getenv("MINIO_SECURE", "False").lower() == "true"

# Initialize MinIO client
minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_SECURE
)

def ensure_bucket_exists():
    """Ensure the bucket exists, create if it doesn't"""
    try:
        if not minio_client.bucket_exists(MINIO_BUCKET):
            minio_client.make_bucket(MINIO_BUCKET)
            # Set public read policy for the bucket
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": "*"},
                        "Action": ["s3:GetObject"],
                        "Resource": [f"arn:aws:s3:::{MINIO_BUCKET}/*"]
                    }
                ]
            }
            minio_client.set_bucket_policy(MINIO_BUCKET, json.dumps(policy))
    except S3Error as e:
        print(f"Error ensuring bucket exists: {e}")

def upload_file(file_data: bytes, filename: str, content_type: str = "application/octet-stream") -> str:
    """
    Upload a file to MinIO and return the public URL
    
    Args:
        file_data: The file content as bytes
        filename: Original filename
        content_type: MIME type of the file
    
    Returns:
        Public URL of the uploaded file
    """
    ensure_bucket_exists()
    
    # Generate a unique filename
    ext = filename.rsplit('.', 1)[1] if '.' in filename else ''
    unique_filename = f"{uuid4()}.{ext}" if ext else str(uuid4())
    
    # Upload the file
    file_stream = BytesIO(file_data)
    file_size = len(file_data)
    
    minio_client.put_object(
        MINIO_BUCKET,
        unique_filename,
        file_stream,
        file_size,
        content_type=content_type
    )
    
    # Return the public URL (via nginx proxy)
    return f"/uploads/{unique_filename}"

def delete_file(filename: str) -> bool:
    """
    Delete a file from MinIO
    
    Args:
        filename: The filename to delete (without /uploads/ prefix)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        minio_client.remove_object(MINIO_BUCKET, filename)
        return True
    except S3Error as e:
        print(f"Error deleting file: {e}")
        return False
