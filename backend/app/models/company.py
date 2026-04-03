import enum
from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CompanyType(str, enum.Enum):
    BUYER = "buyer"
    SUPPLIER = "supplier"
    DISTRIBUTOR = "distributor"
    MANUFACTURER = "manufacturer"
    CONTRACTOR = "contractor"
    SUBCONTRACTOR = "subcontractor"


class CompanySize(str, enum.Enum):
    SIZE_1_10 = "1-10"
    SIZE_11_50 = "11-50"
    SIZE_51_200 = "51-200"
    SIZE_201_500 = "201-500"
    SIZE_500_PLUS = "500+"


class MemberRole(str, enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"


class VerificationStatusEnum(str, enum.Enum):
    NOT_SUBMITTED = "not_submitted"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    NEEDS_UPDATE = "needs_update"


class Company(Base):
    __tablename__ = "companies"
    __table_args__ = (
        Index("idx_companies_type", "company_type"),
        Index("idx_companies_verification", "verification_status"),
        Index("idx_companies_governorate", "governorate"),
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4())
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    company_type: Mapped[CompanyType] = mapped_column(
        Enum(CompanyType, name="company_type", create_constraint=True),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(Text)
    logo_url: Mapped[str | None] = mapped_column(String(500))
    cover_url: Mapped[str | None] = mapped_column(String(500))
    website: Mapped[str | None] = mapped_column(String(500))
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(20))
    address: Mapped[str | None] = mapped_column(Text)
    city: Mapped[str | None] = mapped_column(String(100))
    governorate: Mapped[str | None] = mapped_column(String(100))
    company_size: Mapped[CompanySize | None] = mapped_column(
        Enum(CompanySize, name="company_size", create_constraint=True),
    )
    year_established: Mapped[int | None] = mapped_column(Integer)
    commercial_reg_no: Mapped[str | None] = mapped_column(String(100))
    tax_id: Mapped[str | None] = mapped_column(String(100))
    verification_status: Mapped[VerificationStatusEnum] = mapped_column(
        Enum(VerificationStatusEnum, name="verification_status", create_constraint=True),
        nullable=False,
        default=VerificationStatusEnum.NOT_SUBMITTED,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    profile_completion: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    members = relationship("CompanyMember", back_populates="company", lazy="selectin")
    services = relationship("CompanyService", back_populates="company", lazy="selectin")
    products = relationship("CompanyProduct", back_populates="company", lazy="selectin")
    certifications = relationship(
        "Certification",
        back_populates="company",
        foreign_keys="Certification.company_id",
    )
    references = relationship(
        "ProjectReference",
        back_populates="company",
        foreign_keys="ProjectReference.company_id",
    )
    media = relationship(
        "ProfileMedia",
        back_populates="company",
        foreign_keys="ProfileMedia.company_id",
    )


class CompanyMember(Base):
    __tablename__ = "company_members"
    __table_args__ = (
        UniqueConstraint("company_id", "user_id", name="uq_company_member"),
        Index("idx_company_members_user", "user_id"),
        Index("idx_company_members_company", "company_id"),
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4())
    )
    company_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[MemberRole] = mapped_column(
        Enum(MemberRole, name="member_role", create_constraint=True),
        nullable=False,
        default=MemberRole.MEMBER,
    )
    title: Mapped[str | None] = mapped_column(String(150))
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    company = relationship("Company", back_populates="members")
    user = relationship("User", back_populates="company_memberships")


class CompanyService(Base):
    __tablename__ = "company_services"
    __table_args__ = (
        UniqueConstraint("company_id", "service_category_id", name="uq_company_service"),
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4())
    )
    company_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    service_category_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("service_categories.id"), nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    company = relationship("Company", back_populates="services")
    service_category = relationship("ServiceCategory")


class CompanyProduct(Base):
    __tablename__ = "company_products"
    __table_args__ = (
        UniqueConstraint("company_id", "product_category_id", name="uq_company_product"),
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4())
    )
    company_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    product_category_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("product_categories.id"), nullable=False
    )
    brand_names: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    company = relationship("Company", back_populates="products")
    product_category = relationship("ProductCategory")


class Certification(Base):
    __tablename__ = "certifications"
    __table_args__ = (
        CheckConstraint(
            "company_id IS NOT NULL OR profile_id IS NOT NULL",
            name="ck_cert_owner",
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
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    issuing_body: Mapped[str | None] = mapped_column(String(255))
    issue_date: Mapped[str | None] = mapped_column(String(20))
    expiry_date: Mapped[str | None] = mapped_column(String(20))
    document_url: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    company = relationship("Company", back_populates="certifications", foreign_keys=[company_id])
    profile = relationship(
        "IndividualProfile", back_populates="certifications", foreign_keys=[profile_id]
    )


class ProjectReference(Base):
    __tablename__ = "project_references"
    __table_args__ = (
        CheckConstraint(
            "company_id IS NOT NULL OR profile_id IS NOT NULL",
            name="ck_ref_owner",
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
    project_name: Mapped[str] = mapped_column(String(255), nullable=False)
    client_name: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    location: Mapped[str | None] = mapped_column(String(255))
    year: Mapped[int | None] = mapped_column(Integer)
    scope: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    company = relationship("Company", back_populates="references", foreign_keys=[company_id])
    profile = relationship(
        "IndividualProfile", back_populates="references", foreign_keys=[profile_id]
    )


class ProfileMedia(Base):
    __tablename__ = "profile_media"
    __table_args__ = (
        CheckConstraint(
            "company_id IS NOT NULL OR profile_id IS NOT NULL",
            name="ck_media_owner",
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
    media_type: Mapped[str] = mapped_column(String(50), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    title: Mapped[str | None] = mapped_column(String(255))
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    company = relationship("Company", back_populates="media", foreign_keys=[company_id])
    profile = relationship(
        "IndividualProfile", back_populates="media", foreign_keys=[profile_id]
    )
