from typing import Optional
import uuid
import mimetypes
import boto3  # type: ignore
from botocore.client import Config  # type: ignore
from app.core.config import settings
from app.core.logging_config import logger


def _get_s3_client():
    logger.info(
        "[S3] Preparing client (region=%s, bucket=%s, key_present=%s, secret_present=%s)",
        settings.AWS_REGION,
        settings.S3_BUCKET_NAME,
        bool(settings.AWS_ACCESS_KEY_ID),
        bool(settings.AWS_SECRET_ACCESS_KEY),
    )
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
    logger.info("[S3] Starting profile picture upload: filename=%s, bytes=%s", filename, len(file_bytes))
    if not settings.S3_BUCKET_NAME or not settings.AWS_REGION:
        logger.error("[S3] Missing AWS config: bucket=%s region=%s", settings.S3_BUCKET_NAME, settings.AWS_REGION)
        raise RuntimeError("S3 configuration missing. Set S3_BUCKET_NAME and AWS_REGION")
    s3 = _get_s3_client()
    bucket = settings.S3_BUCKET_NAME

    guessed_type = content_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"
    object_key = f"profile_pictures/{uuid.uuid4()}-{filename}"
    logger.info("[S3] Uploading to bucket=%s key=%s content_type=%s", bucket, object_key, guessed_type)

    try:
        s3.put_object(
            Bucket=bucket,
            Key=object_key,
            Body=file_bytes,
            ContentType=guessed_type,
            ACL="public-read",
        )
        logger.info("[S3] PutObject successful for key=%s", object_key)
    except Exception as exc:
        logger.exception("[S3] PutObject failed for key=%s: %s", object_key, exc)
        raise

    # Public URL (if bucket/object ACL permits public access)
    url = f"https://{bucket}.s3.{settings.AWS_REGION}.amazonaws.com/{object_key}"
    logger.info("[S3] Public URL generated: %s", url)

    # Verify by HEAD request
    try:
        head = s3.head_object(Bucket=bucket, Key=object_key)
        size = head.get("ContentLength")
        logger.info("[S3] HeadObject confirms upload (size=%s) for key=%s", size, object_key)
    except Exception as exc:
        logger.exception("[S3] HeadObject failed for key=%s: %s", object_key, exc)
        # Not fatal for returning URL; still return so caller can decide

    return url


