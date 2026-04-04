from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.auth.schemas import MessageResponse
from app.dependencies import get_db
from app.rfqs.repository import RFQRepository
from app.rfqs.schemas import (
    RFQAwardRequest,
    RFQCreateRequest,
    RFQDetailResponse,
    RFQInviteRequest,
    RFQListResponse,
    RFQResponseCreateRequest,
    RFQResponseResponse,
    RFQResponseUpdateRequest,
    RFQSummaryResponse,
    RFQUpdateRequest,
    RFQAttachmentResponse,
    RFQInvitationResponse,
)
from app.rfqs.service import RFQService

router = APIRouter()


def _get_service(db: Annotated[AsyncSession, Depends(get_db)]) -> RFQService:
    return RFQService(RFQRepository(db), db)


@router.post("/", response_model=RFQDetailResponse, status_code=201)
async def create_rfq(
    body: RFQCreateRequest,
    user: CurrentUser,
    service: Annotated[RFQService, Depends(_get_service)],
    company_id: str = Query(..., description="Buyer company ID"),
):
    rfq = await service.create_rfq(user, company_id, **body.model_dump())
    return RFQDetailResponse.from_rfq(rfq)


@router.get("/", response_model=RFQListResponse)
async def list_rfqs(
    user: CurrentUser,
    service: Annotated[RFQService, Depends(_get_service)],
    company_id: str = Query(..., description="Company ID"),
    role: str = Query("buyer", description="'buyer' for sent RFQs, 'supplier' for received"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = None,
):
    rfqs, counts, total = await service.list_rfqs(
        user, role, company_id, page=page, page_size=page_size, status=status,
    )
    items = [
        RFQSummaryResponse.from_rfq(rfq, count)
        for rfq, count in zip(rfqs, counts)
    ]
    return RFQListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{rfq_id}", response_model=RFQDetailResponse)
async def get_rfq(
    rfq_id: str,
    user: CurrentUser,
    service: Annotated[RFQService, Depends(_get_service)],
):
    rfq = await service.get_rfq(rfq_id, user)
    return RFQDetailResponse.from_rfq(rfq)


@router.patch("/{rfq_id}", response_model=RFQDetailResponse)
async def update_rfq(
    rfq_id: str,
    body: RFQUpdateRequest,
    user: CurrentUser,
    service: Annotated[RFQService, Depends(_get_service)],
):
    rfq = await service.update_rfq(rfq_id, user, **body.model_dump(exclude_unset=True))
    return RFQDetailResponse.from_rfq(rfq)


@router.post("/{rfq_id}/publish", response_model=RFQDetailResponse)
async def publish_rfq(
    rfq_id: str,
    user: CurrentUser,
    service: Annotated[RFQService, Depends(_get_service)],
):
    rfq = await service.publish_rfq(rfq_id, user)
    return RFQDetailResponse.from_rfq(rfq)


@router.post("/{rfq_id}/close", response_model=RFQDetailResponse)
async def close_rfq(
    rfq_id: str,
    user: CurrentUser,
    service: Annotated[RFQService, Depends(_get_service)],
):
    rfq = await service.close_rfq(rfq_id, user)
    return RFQDetailResponse.from_rfq(rfq)


@router.post("/{rfq_id}/cancel", response_model=RFQDetailResponse)
async def cancel_rfq(
    rfq_id: str,
    user: CurrentUser,
    service: Annotated[RFQService, Depends(_get_service)],
):
    rfq = await service.cancel_rfq(rfq_id, user)
    return RFQDetailResponse.from_rfq(rfq)


@router.post("/{rfq_id}/award", response_model=RFQDetailResponse)
async def award_rfq(
    rfq_id: str,
    body: RFQAwardRequest,
    user: CurrentUser,
    service: Annotated[RFQService, Depends(_get_service)],
):
    rfq = await service.award_rfq(rfq_id, user, body.company_id)
    return RFQDetailResponse.from_rfq(rfq)


@router.post("/{rfq_id}/invite", response_model=list[RFQInvitationResponse])
async def invite_companies(
    rfq_id: str,
    body: RFQInviteRequest,
    user: CurrentUser,
    service: Annotated[RFQService, Depends(_get_service)],
):
    invitations = await service.invite_companies(rfq_id, user, body.company_ids)
    return [RFQInvitationResponse.from_invitation(i) for i in invitations]


@router.get("/{rfq_id}/invitations", response_model=list[RFQInvitationResponse])
async def list_invitations(
    rfq_id: str,
    user: CurrentUser,
    service: Annotated[RFQService, Depends(_get_service)],
):
    rfq = await service.get_rfq(rfq_id, user)
    return [RFQInvitationResponse.from_invitation(i) for i in rfq.invitations]


@router.get("/{rfq_id}/responses", response_model=list[RFQResponseResponse])
async def list_responses(
    rfq_id: str,
    user: CurrentUser,
    service: Annotated[RFQService, Depends(_get_service)],
):
    responses = await service.list_responses(rfq_id, user)
    return [RFQResponseResponse.from_response(r) for r in responses]


@router.post("/{rfq_id}/responses", response_model=RFQResponseResponse, status_code=201)
async def submit_response(
    rfq_id: str,
    body: RFQResponseCreateRequest,
    user: CurrentUser,
    service: Annotated[RFQService, Depends(_get_service)],
):
    response = await service.submit_response(rfq_id, user, **body.model_dump())
    return RFQResponseResponse.from_response(response)


@router.patch("/{rfq_id}/responses/{response_id}", response_model=RFQResponseResponse)
async def update_response(
    rfq_id: str,
    response_id: str,
    body: RFQResponseUpdateRequest,
    user: CurrentUser,
    service: Annotated[RFQService, Depends(_get_service)],
):
    response = await service.update_response(
        rfq_id, response_id, user, **body.model_dump(exclude_unset=True)
    )
    return RFQResponseResponse.from_response(response)


@router.post("/{rfq_id}/attachments", response_model=RFQAttachmentResponse, status_code=201)
async def add_attachment(
    rfq_id: str,
    user: CurrentUser,
    service: Annotated[RFQService, Depends(_get_service)],
    file_url: str = Query(...),
    file_name: str = Query(...),
    file_size: int | None = None,
):
    att = await service.add_attachment(rfq_id, user, file_url, file_name, file_size)
    return RFQAttachmentResponse.from_attachment(att)
