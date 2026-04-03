from datetime import datetime, timezone

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.message import (
    Message,
    MessageAttachment,
    MessageParticipant,
    MessageThread,
)


class MessageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_thread(self, thread: MessageThread) -> MessageThread:
        self.db.add(thread)
        await self.db.flush()
        return thread

    async def add_participant(self, participant: MessageParticipant) -> MessageParticipant:
        self.db.add(participant)
        await self.db.flush()
        return participant

    async def create_message(self, message: Message) -> Message:
        self.db.add(message)
        await self.db.flush()
        return message

    async def add_attachment(self, attachment: MessageAttachment) -> MessageAttachment:
        self.db.add(attachment)
        await self.db.flush()
        return attachment

    async def get_thread_by_id(self, thread_id: str) -> MessageThread | None:
        result = await self.db.execute(
            select(MessageThread)
            .options(
                selectinload(MessageThread.participants).selectinload(MessageParticipant.user),
            )
            .where(MessageThread.id == thread_id)
        )
        return result.scalar_one_or_none()

    async def get_thread_messages(
        self, thread_id: str, limit: int = 100, before: str | None = None,
    ) -> list[Message]:
        query = (
            select(Message)
            .options(
                selectinload(Message.sender),
                selectinload(Message.attachments),
            )
            .where(Message.thread_id == thread_id)
        )
        if before:
            query = query.where(Message.created_at < before)
        query = query.order_by(Message.created_at.asc()).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_last_message(self, thread_id: str) -> Message | None:
        result = await self.db.execute(
            select(Message)
            .options(selectinload(Message.sender), selectinload(Message.attachments))
            .where(Message.thread_id == thread_id)
            .order_by(Message.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def list_user_threads(self, user_id: str) -> list[MessageThread]:
        # Get thread IDs where user is participant
        thread_ids = (
            select(MessageParticipant.thread_id)
            .where(MessageParticipant.user_id == user_id)
        )
        result = await self.db.execute(
            select(MessageThread)
            .options(
                selectinload(MessageThread.participants).selectinload(MessageParticipant.user),
            )
            .where(MessageThread.id.in_(thread_ids))
            .order_by(MessageThread.updated_at.desc())
        )
        return list(result.scalars().all())

    async def is_participant(self, thread_id: str, user_id: str) -> bool:
        result = await self.db.execute(
            select(func.count()).select_from(MessageParticipant)
            .where(
                MessageParticipant.thread_id == thread_id,
                MessageParticipant.user_id == user_id,
            )
        )
        return result.scalar_one() > 0

    async def get_participant(self, thread_id: str, user_id: str) -> MessageParticipant | None:
        result = await self.db.execute(
            select(MessageParticipant).where(
                MessageParticipant.thread_id == thread_id,
                MessageParticipant.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def count_unread(self, thread_id: str, user_id: str) -> int:
        participant = await self.get_participant(thread_id, user_id)
        if not participant or not participant.last_read_at:
            result = await self.db.execute(
                select(func.count()).select_from(Message)
                .where(
                    Message.thread_id == thread_id,
                    Message.sender_id != user_id,
                )
            )
            return result.scalar_one()

        result = await self.db.execute(
            select(func.count()).select_from(Message)
            .where(
                Message.thread_id == thread_id,
                Message.sender_id != user_id,
                Message.created_at > participant.last_read_at,
            )
        )
        return result.scalar_one()
