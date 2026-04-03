from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile, File, Query

from app.auth.dependencies import CurrentUser
from app.storage.s3 import upload_file, generate_presigned_url
from app.storage.schemas import UploadResponse
from app.exceptions import BadRequestError

router = APIRouter()


@router.post("/", response_model=UploadResponse, status_code=201)
async def upload(
    user: CurrentUser,
    file: UploadFile = File(...),
    folder: str = Query("uploads", max_length=100),
):
    content = await file.read()
    if not content:
        raise BadRequestError("Empty file")

    try:
        key = upload_file(
            file_content=content,
            original_filename=file.filename or "unknown",
            folder=folder,
            content_type=file.content_type,
        )
    except ValueError as e:
        raise BadRequestError(str(e))

    url = generate_presigned_url(key)
    return UploadResponse(
        key=key,
        url=url,
        file_name=file.filename or "unknown",
        file_size=len(content),
        content_type=file.content_type,
    )


@router.get("/presigned/{key:path}")
async def get_presigned_url(
    key: str,
    user: CurrentUser,
    expires_in: int = Query(3600, ge=60, le=86400),
):
    url = generate_presigned_url(key, expires_in=expires_in)
    return {"url": url, "key": key, "expires_in": expires_in}
