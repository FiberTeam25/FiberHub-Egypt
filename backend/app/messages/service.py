from datetime import datetime, timezone

from app.exceptions import ForbiddenError, NotFoundError
from app.models.message import Message, MessageAttachment, MessageParticipant, MessageThread, ThreadContextType
from app.models.notification import NotificationType
from app.models.user import User
from app.messages.repository import MessageRepository
from app.workers.notifications import create_notification


class MessageService:
    def __init__(self, repo: MessageRepository):
        self.repo = repo

    async def create_thread(
        self,
        user: User,
        context_type: ThreadContextType,
        context_id: str | None,
        subject: str | None,
        participant_user_ids: list[str],
        initial_message: str,
    ) -> MessageThread:
        thread = MessageThread(
            context_type=context_type,
            context_id=context_id,
            subject=subject,
        )
        thread = await self.repo.create_thread(thread)

        # Add creator as participant
        all_participants = set(participant_user_ids) | {user.id}
        for uid in all_participants:
            await self.repo.add_participant(MessageParticipant(
                thread_id=thread.id,
                user_id=uid,
            ))

        # Send initial message
        msg = Message(
            thread_id=thread.id,
            sender_id=user.id,
            content=initial_message,
        )
        await self.repo.create_message(msg)

        # Notify other participants
        for uid in participant_user_ids:
            if uid != user.id:
                await create_notification(
                    self.repo.db, uid,
                    NotificationType.NEW_MESSAGE,
                    f"New message from {user.full_name}",
                    initial_message[:100],
                    link=f"/messages/{thread.id}",
                )

        await self.repo.db.flush()
        return await self.repo.get_thread_by_id(thread.id)

    async def get_thread(self, thread_id: str, user: User):
        thread = await self.repo.get_thread_by_id(thread_id)
        if not thread:
            raise NotFoundError("Thread not found")
        if not await self.repo.is_participant(thread_id, user.id):
            raise ForbiddenError("You are not a participant in this thread")
        return thread

    async def get_thread_with_messages(self, thread_id: str, user: User):
        thread = await self.get_thread(thread_id, user)
        messages = await self.repo.get_thread_messages(thread_id)
        return thread, messages

    async def list_threads(self, user: User):
        threads = await self.repo.list_user_threads(user.id)
        result = []
        for thread in threads:
            last_msg = await self.repo.get_last_message(thread.id)
            unread = await self.repo.count_unread(thread.id, user.id)
            result.append((thread, last_msg, unread))
        return result

    async def send_message(
        self, thread_id: str, user: User, content: str
    ) -> Message:
        if not await self.repo.is_participant(thread_id, user.id):
            raise ForbiddenError("You are not a participant in this thread")

        msg = Message(
            thread_id=thread_id,
            sender_id=user.id,
            content=content,
        )
        msg = await self.repo.create_message(msg)

        # Update thread timestamp
        thread = await self.repo.get_thread_by_id(thread_id)
        thread.updated_at = datetime.now(timezone.utc)

        # Notify other participants
        for participant in thread.participants:
            if participant.user_id != user.id:
                await create_notification(
                    self.repo.db, participant.user_id,
                    NotificationType.NEW_MESSAGE,
                    f"New message from {user.full_name}",
                    content[:100],
                    link=f"/messages/{thread_id}",
                )

        await self.repo.db.flush()

        # Reload with sender and attachments by specific ID (avoids race condition)
        return await self.repo.get_message_by_id(msg.id)

    async def mark_as_read(self, thread_id: str, user: User) -> None:
        if not await self.repo.is_participant(thread_id, user.id):
            raise ForbiddenError("You are not a participant in this thread")

        participant = await self.repo.get_participant(thread_id, user.id)
        if participant:
            participant.last_read_at = datetime.now(timezone.utc)
            await self.repo.db.flush()

    async def add_attachment(
        self, thread_id: str, message_id: str, user: User,
        file_url: str, file_name: str, file_size: int | None,
    ) -> MessageAttachment:
        if not await self.repo.is_participant(thread_id, user.id):
            raise ForbiddenError("You are not a participant in this thread")

        att = MessageAttachment(
            message_id=message_id,
            file_url=file_url,
            file_name=file_name,
            file_size=file_size,
        )
        return await self.repo.add_attachment(att)
