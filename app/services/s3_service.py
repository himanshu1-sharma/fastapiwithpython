from typing import Optional
import uuid
import mimetypes
import boto3  # type: ignore
from botocore.client import Config  # type: ignore
from app.core.config import settings


def _get_s3_client():
    return boto3.client(
        "s3",
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        config=Config(signature_version="s3v4"),
    )


def upload_user_profile_picture(file_bytes: bytes, filename: str, content_type: Optional[str] = None) -> str:
    """Uploads file bytes to S3 under a unique key and returns the public URL.

    The object is uploaded with ACL private; URL returned is a virtual-hosted–style public URL
    assuming the bucket has public-read policy or CloudFront in front. Adjust as needed.
    """
    s3 = _get_s3_client()
    bucket = settings.S3_BUCKET_NAME

    guessed_type = content_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"
    object_key = f"profile_pictures/{uuid.uuid4()}-{filename}"

    s3.put_object(
        Bucket=bucket,
        Key=object_key,
        Body=file_bytes,
        ContentType=guessed_type,
        ACL="public-read",
    )

    # Public URL (if bucket/object ACL permits public access)
    url = f"https://{bucket}.s3.{settings.AWS_REGION}.amazonaws.com/{object_key}"
    return url


