import re
import uuid

import boto3
from fastapi import HTTPException, status

from app.config import settings

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif", "image/avif"}


def _client():
    return boto3.client(
        "s3",
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id or None,
        aws_secret_access_key=settings.aws_secret_access_key or None,
    )


def create_presigned_upload(filename: str, content_type: str) -> dict:
    if not settings.s3_bucket:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="S3 is not configured (S3_BUCKET missing)",
        )
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported content type: {content_type}",
        )
    safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", filename)
    key = f"{settings.s3_upload_prefix}/{uuid.uuid4().hex}_{safe_name}"

    upload_url = _client().generate_presigned_url(
        "put_object",
        Params={
            "Bucket": settings.s3_bucket,
            "Key": key,
            "ContentType": content_type,
        },
        ExpiresIn=600,
    )
    public_url = f"https://{settings.s3_bucket}.s3.{settings.aws_region}.amazonaws.com/{key}"
    return {"upload_url": upload_url, "public_url": public_url, "key": key}
