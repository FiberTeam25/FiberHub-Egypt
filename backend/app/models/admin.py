import enum
from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SAEnum

from app.database import Base


class AdminActionType(str, enum.Enum):
    VERIFY_APPROVE = "verify_approve"
    VERIFY_REJECT = "verify_reject"
    USER_SUSPEND = "user_suspend"
    USER_ACTIVATE = "user_activate"
    REVIEW_REMOVE = "review_remove"
    COMPANY_FLAG = "company_flag"
    CATEGORY_UPDATE = "category_update"


class AdminActionLog(Base):
    __tablename__ = "admin_action_logs"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4())
    )
    admin_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id"), nullable=False
    )
    action_type: Mapped[AdminActionType] = mapped_column(
        SAEnum(AdminActionType, name="admin_action_type", create_constraint=True),
        nullable=False,
    )
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    details: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    admin = relationship("User")


class Shortlist(Base):
    __tablename__ = "shortlists"
    __table_args__ = (
        CheckConstraint(
            "company_id IS NOT NULL OR profile_id IS NOT NULL",
            name="ck_shortlist_target",
        ),
        Index("idx_shortlists_user", "user_id"),
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    company_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("companies.id", ondelete="CASCADE")
    )
    profile_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("individual_profiles.id", ondelete="CASCADE")
    )
    note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user = relationship("User")
    company = relationship("Company")
    profile = relationship("IndividualProfile")
