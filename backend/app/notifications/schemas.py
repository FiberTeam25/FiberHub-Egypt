from pydantic import BaseModel

from app.models.notification import NotificationType


class NotificationResponse(BaseModel):
    id: str
    type: NotificationType
    title: str
    body: str | None
    link: str | None
    is_read: bool
    created_at: str

    @classmethod
    def from_notification(cls, notif) -> "NotificationResponse":
        return cls(
            id=notif.id,
            type=notif.type,
            title=notif.title,
            body=notif.body,
            link=notif.link,
            is_read=notif.is_read,
            created_at=notif.created_at.isoformat(),
        )


class NotificationListResponse(BaseModel):
    items: list[NotificationResponse]
    total: int
    page: int
    page_size: int
    unread_count: int


class UnreadCountResponse(BaseModel):
    unread_count: int
