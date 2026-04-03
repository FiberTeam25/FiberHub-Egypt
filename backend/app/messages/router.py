from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.auth.schemas import MessageResponse as MsgResponse
from app.dependencies import get_db
from app.messages.repository import MessageRepository
from app.messages.schemas import (
    AttachmentResponse,
    MessageResponse,
    MessageSendRequest,
    ThreadCreateRequest,
    ThreadDetailResponse,
    ThreadListResponse,
    ThreadResponse,
)
from app.messages.service import MessageService

router = APIRouter()


def _get_service(db: Annotated[AsyncSession, Depends(get_db)]) -> MessageService:
    return MessageService(MessageRepository(db))


@router.get("/threads", response_model=ThreadListResponse)
async def list_threads(
    user: CurrentUser,
    service: Annotated[MessageService, Depends(_get_service)],
):
    thread_data = await service.list_threads(user)
    items = [
        ThreadResponse.from_thread(thread, last_msg, unread)
        for thread, last_msg, unread in thread_data
    ]
    return ThreadListResponse(items=items, total=len(items))


@router.post("/threads", response_model=ThreadResponse, status_code=201)
async def create_thread(
    body: ThreadCreateRequest,
    user: CurrentUser,
    service: Annotated[MessageService, Depends(_get_service)],
):
    thread = await service.create_thread(
        user=user,
        context_type=body.context_type,
        context_id=body.context_id,
        subject=body.subject,
        participant_user_ids=body.participant_user_ids,
        initial_message=body.initial_message,
    )
    last_msg = None
    if thread.messages:
        last_msg = thread.messages[-1] if hasattr(thread, 'messages') else None
    return ThreadResponse.from_thread(thread, last_msg, 0)


@router.get("/threads/{thread_id}", response_model=ThreadDetailResponse)
async def get_thread(
    thread_id: str,
    user: CurrentUser,
    service: Annotated[MessageService, Depends(_get_service)],
):
    thread, messages = await service.get_thread_with_messages(thread_id, user)
    unread = 0  # User is viewing, about to mark read
    return ThreadDetailResponse(
        thread=ThreadResponse.from_thread(thread, messages[-1] if messages else None, unread),
        messages=[MessageResponse.from_message(m) for m in messages],
    )


@router.post("/threads/{thread_id}/messages", response_model=MessageResponse)
async def send_message(
    thread_id: str,
    body: MessageSendRequest,
    user: CurrentUser,
    service: Annotated[MessageService, Depends(_get_service)],
):
    msg = await service.send_message(thread_id, user, body.content)
    return MessageResponse.from_message(msg)


@router.post("/threads/{thread_id}/read", response_model=MsgResponse)
async def mark_thread_read(
    thread_id: str,
    user: CurrentUser,
    service: Annotated[MessageService, Depends(_get_service)],
):
    await service.mark_as_read(thread_id, user)
    return MsgResponse(message="Thread marked as read")


@router.post(
    "/threads/{thread_id}/messages/{message_id}/attachments",
    response_model=AttachmentResponse,
    status_code=201,
)
async def add_attachment(
    thread_id: str,
    message_id: str,
    user: CurrentUser,
    service: Annotated[MessageService, Depends(_get_service)],
    file_url: str = Query(...),
    file_name: str = Query(...),
    file_size: int | None = None,
):
    att = await service.add_attachment(
        thread_id, message_id, user, file_url, file_name, file_size,
    )
    return AttachmentResponse.from_attachment(att)
