from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SAEnum, ForeignKey

from app.database import Base
from app.models.company import VerificationStatusEnum


class IndividualProfile(Base):
    __tablename__ = "individual_profiles"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"),
        unique=True, nullable=False,
    )
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    headline: Mapped[str | None] = mapped_column(String(255))
    bio: Mapped[str | None] = mapped_column(Text)
    specializations: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    experience_years: Mapped[int | None] = mapped_column(Integer)
    city: Mapped[str | None] = mapped_column(String(100))
    governorate: Mapped[str | None] = mapped_column(String(100))
    availability: Mapped[str | None] = mapped_column(String(50))
    hourly_rate_egp: Mapped[float | None] = mapped_column(Numeric(10, 2))
    resume_url: Mapped[str | None] = mapped_column(String(500))
    verification_status: Mapped[VerificationStatusEnum] = mapped_column(
        SAEnum(VerificationStatusEnum, name="verification_status", create_constraint=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=VerificationStatusEnum.NOT_SUBMITTED,
    )
    profile_completion: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="individual_profile")
    certifications = relationship(
        "Certification",
        back_populates="profile",
        foreign_keys="Certification.profile_id",
    )
    references = relationship(
        "ProjectReference",
        back_populates="profile",
        foreign_keys="ProjectReference.profile_id",
    )
    media = relationship(
        "ProfileMedia",
        back_populates="profile",
        foreign_keys="ProfileMedia.profile_id",
    )
