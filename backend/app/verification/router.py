from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import AdminUser, CurrentUser
from app.dependencies import get_db
from app.verification.repository import VerificationRepository
from app.verification.schemas import (
    VerificationQueueResponse,
    VerificationRequestResponse,
    VerificationReviewRequest,
    VerificationSubmitRequest,
)
from app.verification.service import VerificationService

router = APIRouter()


def _get_service(db: Annotated[AsyncSession, Depends(get_db)]) -> VerificationService:
    return VerificationService(VerificationRepository(db), db)


@router.post("/submit", response_model=VerificationRequestResponse, status_code=201)
async def submit_verification(
    body: VerificationSubmitRequest,
    user: CurrentUser,
    service: Annotated[VerificationService, Depends(_get_service)],
):
    req = await service.submit_verification(
        user=user,
        company_id=body.company_id,
        profile_id=body.profile_id,
        documents=[d.model_dump() for d in body.documents],
    )
    return VerificationRequestResponse.from_request(req)


@router.get("/status", response_model=VerificationRequestResponse | None)
async def get_verification_status(
    user: CurrentUser,
    service: Annotated[VerificationService, Depends(_get_service)],
    company_id: str | None = None,
    profile_id: str | None = None,
):
    req = await service.get_status(user, company_id, profile_id)
    if not req:
        return None
    return VerificationRequestResponse.from_request(req)


@router.get("/queue", response_model=VerificationQueueResponse)
async def get_verification_queue(
    admin: AdminUser,
    service: Annotated[VerificationService, Depends(_get_service)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = None,
):
    items, total = await service.get_queue(page=page, page_size=page_size, status=status)
    return VerificationQueueResponse(
        items=[VerificationRequestResponse.from_request(r) for r in items],
        total=total, page=page, page_size=page_size,
    )


@router.get("/{request_id}", response_model=VerificationRequestResponse)
async def get_verification_detail(
    request_id: str,
    admin: AdminUser,
    service: Annotated[VerificationService, Depends(_get_service)],
):
    req = await service.get_request_detail(request_id)
    return VerificationRequestResponse.from_request(req)


@router.post("/{request_id}/approve", response_model=VerificationRequestResponse)
async def approve_verification(
    request_id: str,
    body: VerificationReviewRequest,
    admin: AdminUser,
    service: Annotated[VerificationService, Depends(_get_service)],
):
    req = await service.approve(request_id, admin, body.admin_notes)
    return VerificationRequestResponse.from_request(req)


@router.post("/{request_id}/reject", response_model=VerificationRequestResponse)
async def reject_verification(
    request_id: str,
    body: VerificationReviewRequest,
    admin: AdminUser,
    service: Annotated[VerificationService, Depends(_get_service)],
):
    req = await service.reject(request_id, admin, body.admin_notes)
    return VerificationRequestResponse.from_request(req)
