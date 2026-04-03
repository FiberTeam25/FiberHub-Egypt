from app.exceptions import ForbiddenError, NotFoundError
from app.models.notification import Notification
from app.models.user import User
from app.notifications.repository import NotificationRepository


class NotificationService:
    def __init__(self, repo: NotificationRepository):
        self.repo = repo

    async def list_notifications(
        self, user: User, page: int = 1, page_size: int = 20
    ) -> tuple[list[Notification], int, int]:
        items, total = await self.repo.list_by_user(user.id, page, page_size)
        unread_count = await self.repo.count_unread(user.id)
        return items, total, unread_count

    async def get_unread_count(self, user: User) -> int:
        return await self.repo.count_unread(user.id)

    async def mark_read(self, notification_id: str, user: User) -> Notification:
        notif = await self.repo.get_by_id(notification_id)
        if not notif:
            raise NotFoundError("Notification not found")
        if notif.user_id != user.id:
            raise ForbiddenError("Not your notification")
        notif = await self.repo.mark_read(notification_id, user.id)
        return notif

    async def mark_all_read(self, user: User) -> int:
        return await self.repo.mark_all_read(user.id)
