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
        endpoint_url=f"https://s3.{settings.aws_region}.amazonaws.com",
        aws_access_key_id=settings.aws_access_key_id or None,
        aws_secret_access_key=settings.aws_secret_access_key or None,
    )


def build_key(filename: str) -> str:
    """A collision-proof object key for an uploaded file, keeping a readable suffix."""
    safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", filename)
    return f"{settings.s3_upload_prefix}/{uuid.uuid4().hex}_{safe_name}"


def public_url_for(key: str) -> str:
    return f"https://{settings.s3_bucket}.s3.{settings.aws_region}.amazonaws.com/{key}"


def upload_bytes(data: bytes, filename: str, content_type: str) -> str:
    """Server-side upload used by seed scripts; returns the object's public URL.

    The browser path goes through presigned PUTs instead — see
    `create_presigned_upload`.
    """
    if not settings.s3_bucket:
        raise RuntimeError("S3 is not configured (S3_BUCKET missing)")
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise ValueError(f"Unsupported content type: {content_type}")

    key = build_key(filename)
    _client().put_object(
        Bucket=settings.s3_bucket, Key=key, Body=data, ContentType=content_type
    )
    return public_url_for(key)


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
    key = build_key(filename)

    upload_url = _client().generate_presigned_url(
        "put_object",
        Params={
            "Bucket": settings.s3_bucket,
            "Key": key,
            "ContentType": content_type,
        },
        ExpiresIn=600,
    )
    return {"upload_url": upload_url, "public_url": public_url_for(key), "key": key}
