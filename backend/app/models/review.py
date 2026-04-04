import enum
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, SmallInteger, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SAEnum, Index, CheckConstraint

from app.database import Base


class ReviewTargetType(str, enum.Enum):
    COMPANY = "company"
    INDIVIDUAL = "individual"


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (
        Index("idx_reviews_target_company", "target_company_id"),
        CheckConstraint("overall_rating BETWEEN 1 AND 5", name="ck_overall_rating"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    reviewer_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    reviewer_company_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("companies.id")
    )
    target_type: Mapped[ReviewTargetType] = mapped_column(
        SAEnum(ReviewTargetType, name="review_target_type", create_constraint=True, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    target_company_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("companies.id")
    )
    target_profile_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("individual_profiles.id")
    )
    rfq_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("rfqs.id")
    )
    overall_rating: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    response_speed: Mapped[int | None] = mapped_column(SmallInteger)
    communication: Mapped[int | None] = mapped_column(SmallInteger)
    documentation: Mapped[int | None] = mapped_column(SmallInteger)
    comment: Mapped[str | None] = mapped_column(Text)
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    reviewer = relationship("User", foreign_keys=[reviewer_id])
    flags = relationship("ReviewFlag", back_populates="review")


class ReviewFlag(Base):
    __tablename__ = "review_flags"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    review_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False
    )
    flagged_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    resolved_by: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    review = relationship("Review", back_populates="flags")
