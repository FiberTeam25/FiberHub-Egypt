import os
import uuid
from pathlib import PurePosixPath

import boto3
from botocore.config import Config as BotoConfig

from app.config import get_settings


def get_s3_client():
    settings = get_settings()
    kwargs = {
        "aws_access_key_id": settings.s3_access_key,
        "aws_secret_access_key": settings.s3_secret_key,
        "region_name": settings.s3_region,
        "config": BotoConfig(signature_version="s3v4"),
    }
    if settings.s3_endpoint_url:
        kwargs["endpoint_url"] = settings.s3_endpoint_url
    return boto3.client("s3", **kwargs)


def upload_file(
    file_content: bytes,
    original_filename: str,
    folder: str = "uploads",
    content_type: str | None = None,
) -> str:
    """Upload a file to S3. Returns the object key."""
    settings = get_settings()
    ext = PurePosixPath(original_filename).suffix.lower()

    # Validate file type
    if ext not in settings.allowed_file_type_list:
        raise ValueError(f"File type {ext} is not allowed")

    # Validate file size
    if len(file_content) > settings.max_file_size_bytes:
        raise ValueError(f"File exceeds maximum size of {settings.max_file_size_mb}MB")

    # Generate unique key
    unique_name = f"{uuid.uuid4().hex}{ext}"
    key = f"{folder}/{unique_name}"

    client = get_s3_client()
    extra_args = {}
    if content_type:
        extra_args["ContentType"] = content_type

    client.put_object(
        Bucket=settings.s3_bucket_name,
        Key=key,
        Body=file_content,
        **extra_args,
    )

    return key


def generate_presigned_url(key: str, expires_in: int = 3600) -> str:
    """Generate a presigned URL for downloading a file."""
    settings = get_settings()
    client = get_s3_client()
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.s3_bucket_name, "Key": key},
        ExpiresIn=expires_in,
    )


def delete_file(key: str) -> None:
    """Delete a file from S3."""
    settings = get_settings()
    client = get_s3_client()
    client.delete_object(Bucket=settings.s3_bucket_name, Key=key)
