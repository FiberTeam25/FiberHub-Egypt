import enum
from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SAEnum

from app.database import Base


class RFQStatus(str, enum.Enum):
    DRAFT = "draft"
    OPEN = "open"
    CLOSED = "closed"
    AWARDED = "awarded"
    CANCELLED = "cancelled"


class RFQResponseStatus(str, enum.Enum):
    INVITED = "invited"
    VIEWED = "viewed"
    SUBMITTED = "submitted"
    REVISED = "revised"
    WITHDRAWN = "withdrawn"


class RFQ(Base):
    __tablename__ = "rfqs"
    __table_args__ = (
        Index("idx_rfqs_company", "company_id"),
        Index("idx_rfqs_status", "status"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    company_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("companies.id"), nullable=False
    )
    created_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    request_type: Mapped[str] = mapped_column(String(100), nullable=False)
    category_id: Mapped[str | None] = mapped_column(String(36))
    category_type: Mapped[str | None] = mapped_column(String(20))
    description: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str | None] = mapped_column(String(255))
    governorate: Mapped[str | None] = mapped_column(String(100))
    quantity_scope: Mapped[str | None] = mapped_column(Text)
    timeline: Mapped[str | None] = mapped_column(String(255))
    deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    status: Mapped[RFQStatus] = mapped_column(
        SAEnum(RFQStatus, name="rfq_status", create_constraint=True, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=RFQStatus.DRAFT,
    )
    awarded_to: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("companies.id")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    buyer_company = relationship("Company", foreign_keys=[company_id])
    creator = relationship("User", foreign_keys=[created_by])
    attachments = relationship("RFQAttachment", back_populates="rfq", lazy="selectin")
    invitations = relationship("RFQInvitation", back_populates="rfq", lazy="selectin")
    responses = relationship("RFQResponse", back_populates="rfq")
    status_history = relationship("RFQStatusHistory", back_populates="rfq")


class RFQAttachment(Base):
    __tablename__ = "rfq_attachments"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    rfq_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("rfqs.id", ondelete="CASCADE"), nullable=False
    )
    file_url: Mapped[str] = mapped_column(String(500), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size: Mapped[int | None] = mapped_column(Integer)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    rfq = relationship("RFQ", back_populates="attachments")


class RFQInvitation(Base):
    __tablename__ = "rfq_invitations"
    __table_args__ = (
        UniqueConstraint("rfq_id", "company_id", name="uq_rfq_invitation"),
        Index("idx_rfq_invitations_company", "company_id"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    rfq_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("rfqs.id", ondelete="CASCADE"), nullable=False
    )
    company_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("companies.id"), nullable=False
    )
    status: Mapped[RFQResponseStatus] = mapped_column(
        SAEnum(RFQResponseStatus, name="rfq_response_status", create_constraint=True, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=RFQResponseStatus.INVITED,
    )
    invited_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    viewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    rfq = relationship("RFQ", back_populates="invitations")
    company = relationship("Company")


class RFQResponse(Base):
    __tablename__ = "rfq_responses"
    __table_args__ = (
        UniqueConstraint("rfq_id", "company_id", name="uq_rfq_response"),
        Index("idx_rfq_responses_rfq", "rfq_id"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    rfq_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("rfqs.id", ondelete="CASCADE"), nullable=False
    )
    company_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("companies.id"), nullable=False
    )
    submitted_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    cover_note: Mapped[str | None] = mapped_column(Text)
    quoted_amount: Mapped[float | None] = mapped_column(Numeric(15, 2))
    currency: Mapped[str] = mapped_column(String(10), default="EGP")
    delivery_time: Mapped[str | None] = mapped_column(String(255))
    notes: Mapped[str | None] = mapped_column(Text)
    file_url: Mapped[str | None] = mapped_column(String(500))
    file_name: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[RFQResponseStatus] = mapped_column(
        SAEnum(RFQResponseStatus, name="rfq_response_status", create_constraint=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=RFQResponseStatus.SUBMITTED,
    )
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    rfq = relationship("RFQ", back_populates="responses")
    company = relationship("Company")
    submitter = relationship("User")


class RFQStatusHistory(Base):
    __tablename__ = "rfq_status_history"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    rfq_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("rfqs.id", ondelete="CASCADE"), nullable=False
    )
    old_status: Mapped[RFQStatus | None] = mapped_column(
        SAEnum(RFQStatus, name="rfq_status", create_constraint=False, values_callable=lambda x: [e.value for e in x])
    )
    new_status: Mapped[RFQStatus] = mapped_column(
        SAEnum(RFQStatus, name="rfq_status", create_constraint=False, values_callable=lambda x: [e.value for e in x]), nullable=False
    )
    changed_by: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id")
    )
    note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    rfq = relationship("RFQ", back_populates="status_history")
