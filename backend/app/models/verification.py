from datetime import datetime
from uuid import uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SAEnum

from app.database import Base
from app.models.company import VerificationStatusEnum


class VerificationRequest(Base):
    __tablename__ = "verification_requests"
    __table_args__ = (
        CheckConstraint(
            "company_id IS NOT NULL OR profile_id IS NOT NULL",
            name="ck_verif_owner",
        ),
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4())
    )
    company_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("companies.id", ondelete="CASCADE")
    )
    profile_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("individual_profiles.id", ondelete="CASCADE")
    )
    status: Mapped[VerificationStatusEnum] = mapped_column(
        SAEnum(VerificationStatusEnum, name="verification_status", create_constraint=False),
        nullable=False,
        default=VerificationStatusEnum.PENDING,
    )
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reviewed_by: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id")
    )
    admin_notes: Mapped[str | None] = mapped_column(Text)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    documents = relationship("VerificationDocument", back_populates="request", lazy="selectin")


class VerificationDocument(Base):
    __tablename__ = "verification_documents"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4())
    )
    verification_request_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("verification_requests.id", ondelete="CASCADE"),
        nullable=False,
    )
    document_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_url: Mapped[str] = mapped_column(String(500), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    request = relationship("VerificationRequest", back_populates="documents")
