"""
Notification dispatch service.

Creates in-app notifications and optionally triggers email notifications.
"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification, NotificationType

logger = logging.getLogger(__name__)


async def create_notification(
    db: AsyncSession,
    user_id: str,
    notification_type: NotificationType,
    title: str,
    body: str | None = None,
    link: str | None = None,
) -> Notification:
    """Create an in-app notification."""
    notification = Notification(
        user_id=user_id,
        type=notification_type,
        title=title,
        body=body,
        link=link,
    )
    db.add(notification)
    await db.flush()

    logger.info("Notification created for user %s: %s", user_id, title)
    return notification
