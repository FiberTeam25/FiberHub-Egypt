from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.dependencies import get_db
from app.notifications.repository import NotificationRepository
from app.notifications.schemas import (
    NotificationListResponse,
    NotificationResponse,
    UnreadCountResponse,
)
from app.notifications.service import NotificationService

router = APIRouter()


def _get_service(db: Annotated[AsyncSession, Depends(get_db)]) -> NotificationService:
    return NotificationService(NotificationRepository(db))


@router.get("/", response_model=NotificationListResponse)
async def list_notifications(
    user: CurrentUser,
    service: Annotated[NotificationService, Depends(_get_service)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    items, total, unread_count = await service.list_notifications(user, page, page_size)
    return NotificationListResponse(
        items=[NotificationResponse.from_notification(n) for n in items],
        total=total,
        page=page,
        page_size=page_size,
        unread_count=unread_count,
    )


@router.get("/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
    user: CurrentUser,
    service: Annotated[NotificationService, Depends(_get_service)],
):
    count = await service.get_unread_count(user)
    return UnreadCountResponse(unread_count=count)


@router.post("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: str,
    user: CurrentUser,
    service: Annotated[NotificationService, Depends(_get_service)],
):
    notif = await service.mark_read(notification_id, user)
    return NotificationResponse.from_notification(notif)


@router.post("/read-all")
async def mark_all_notifications_read(
    user: CurrentUser,
    service: Annotated[NotificationService, Depends(_get_service)],
):
    count = await service.mark_all_read(user)
    return {"message": f"Marked {count} notifications as read"}
