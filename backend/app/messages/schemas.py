from pydantic import BaseModel, Field

from app.models.message import ThreadContextType


class ThreadCreateRequest(BaseModel):
    context_type: ThreadContextType = ThreadContextType.DIRECT
    context_id: str | None = None
    subject: str | None = Field(None, max_length=255)
    participant_user_ids: list[str]
    initial_message: str = Field(min_length=1)


class MessageSendRequest(BaseModel):
    content: str = Field(min_length=1)


class AttachmentResponse(BaseModel):
    id: str
    file_url: str
    file_name: str
    file_size: int | None
    created_at: str

    @classmethod
    def from_attachment(cls, att) -> "AttachmentResponse":
        return cls(
            id=att.id, file_url=att.file_url, file_name=att.file_name,
            file_size=att.file_size, created_at=att.created_at.isoformat(),
        )


class MessageResponse(BaseModel):
    id: str
    thread_id: str
    sender_id: str
    sender_name: str | None = None
    content: str
    attachments: list[AttachmentResponse]
    created_at: str

    @classmethod
    def from_message(cls, msg) -> "MessageResponse":
        return cls(
            id=msg.id,
            thread_id=msg.thread_id,
            sender_id=msg.sender_id,
            sender_name=msg.sender.full_name if msg.sender else None,
            content=msg.content,
            attachments=[AttachmentResponse.from_attachment(a) for a in (msg.attachments or [])],
            created_at=msg.created_at.isoformat(),
        )


class ParticipantResponse(BaseModel):
    user_id: str
    user_name: str | None = None
    company_id: str | None
    last_read_at: str | None

    @classmethod
    def from_participant(cls, p) -> "ParticipantResponse":
        return cls(
            user_id=p.user_id,
            user_name=p.user.full_name if p.user else None,
            company_id=p.company_id,
            last_read_at=p.last_read_at.isoformat() if p.last_read_at else None,
        )


class ThreadResponse(BaseModel):
    id: str
    context_type: ThreadContextType
    context_id: str | None
    subject: str | None
    participants: list[ParticipantResponse]
    last_message: MessageResponse | None = None
    unread_count: int = 0
    created_at: str
    updated_at: str

    @classmethod
    def from_thread(
        cls, thread, last_message=None, unread_count: int = 0
    ) -> "ThreadResponse":
        return cls(
            id=thread.id,
            context_type=thread.context_type,
            context_id=thread.context_id,
            subject=thread.subject,
            participants=[ParticipantResponse.from_participant(p) for p in (thread.participants or [])],
            last_message=MessageResponse.from_message(last_message) if last_message else None,
            unread_count=unread_count,
            created_at=thread.created_at.isoformat(),
            updated_at=thread.updated_at.isoformat(),
        )


class ThreadDetailResponse(BaseModel):
    thread: ThreadResponse
    messages: list[MessageResponse]


class ThreadListResponse(BaseModel):
    items: list[ThreadResponse]
    total: int
