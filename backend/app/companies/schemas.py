from pydantic import BaseModel, EmailStr, Field

from app.models.company import CompanySize, CompanyType, MemberRole, VerificationStatusEnum


class CompanyCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    company_type: CompanyType
    description: str | None = None
    website: str | None = Field(None, max_length=500)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=20)
    address: str | None = None
    city: str | None = Field(None, max_length=100)
    governorate: str | None = Field(None, max_length=100)
    company_size: CompanySize | None = None
    year_established: int | None = None
    commercial_reg_no: str | None = Field(None, max_length=100)
    tax_id: str | None = Field(None, max_length=100)


class CompanyUpdateRequest(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=255)
    description: str | None = None
    website: str | None = Field(None, max_length=500)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=20)
    address: str | None = None
    city: str | None = Field(None, max_length=100)
    governorate: str | None = Field(None, max_length=100)
    company_size: CompanySize | None = None
    year_established: int | None = None
    commercial_reg_no: str | None = Field(None, max_length=100)
    tax_id: str | None = Field(None, max_length=100)


class CompanyResponse(BaseModel):
    id: str
    name: str
    slug: str
    company_type: CompanyType
    description: str | None
    logo_url: str | None
    cover_url: str | None
    website: str | None
    email: str | None
    phone: str | None
    address: str | None
    city: str | None
    governorate: str | None
    company_size: CompanySize | None
    year_established: int | None
    verification_status: VerificationStatusEnum
    profile_completion: int
    created_at: str

    model_config = {"from_attributes": True}

    @classmethod
    def from_company(cls, company) -> "CompanyResponse":
        return cls(
            id=company.id,
            name=company.name,
            slug=company.slug,
            company_type=company.company_type,
            description=company.description,
            logo_url=company.logo_url,
            cover_url=company.cover_url,
            website=company.website,
            email=company.email,
            phone=company.phone,
            address=company.address,
            city=company.city,
            governorate=company.governorate,
            company_size=company.company_size,
            year_established=company.year_established,
            verification_status=company.verification_status,
            profile_completion=company.profile_completion,
            created_at=company.created_at.isoformat(),
        )


class CompanyListResponse(BaseModel):
    items: list[CompanyResponse]
    total: int
    page: int
    page_size: int


class MemberAddRequest(BaseModel):
    email: str
    role: MemberRole = MemberRole.MEMBER
    title: str | None = Field(None, max_length=150)


class MemberUpdateRequest(BaseModel):
    role: MemberRole | None = None
    title: str | None = Field(None, max_length=150)


class MemberResponse(BaseModel):
    id: str
    user_id: str
    first_name: str
    last_name: str
    email: str
    role: MemberRole
    title: str | None
    is_primary: bool
    joined_at: str

    @classmethod
    def from_member(cls, member) -> "MemberResponse":
        return cls(
            id=member.id,
            user_id=member.user_id,
            first_name=member.user.first_name,
            last_name=member.user.last_name,
            email=member.user.email,
            role=member.role,
            title=member.title,
            is_primary=member.is_primary,
            joined_at=member.joined_at.isoformat(),
        )


class CompanyServiceRequest(BaseModel):
    service_category_id: str
    description: str | None = None


class CompanyProductRequest(BaseModel):
    product_category_id: str
    brand_names: list[str] | None = None
    description: str | None = None


class CertificationRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    issuing_body: str | None = Field(None, max_length=255)
    issue_date: str | None = None
    expiry_date: str | None = None
    document_url: str | None = None


class ProjectReferenceRequest(BaseModel):
    project_name: str = Field(min_length=1, max_length=255)
    client_name: str | None = Field(None, max_length=255)
    description: str | None = None
    location: str | None = Field(None, max_length=255)
    year: int | None = None
    scope: str | None = None
