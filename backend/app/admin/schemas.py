from pydantic import BaseModel

from app.models.admin import AdminActionType
from app.models.user import AccountType, UserStatus


class DashboardStatsResponse(BaseModel):
    total_users: int
    total_companies: int
    verified_companies: int
    pending_verifications: int
    flagged_reviews: int


class AdminUserResponse(BaseModel):
    id: str
    email: str
    first_name: str | None
    last_name: str | None
    phone: str | None
    account_type: AccountType
    status: UserStatus
    email_verified: bool
    created_at: str

    @classmethod
    def from_user(cls, user) -> "AdminUserResponse":
        return cls(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            account_type=user.account_type,
            status=user.status,
            email_verified=user.email_verified,
            created_at=user.created_at.isoformat(),
        )


class AdminUserListResponse(BaseModel):
    items: list[AdminUserResponse]
    total: int
    page: int
    page_size: int


class AdminCompanyResponse(BaseModel):
    id: str
    name: str
    slug: str
    company_type: str
    verification_status: str
    is_active: bool
    governorate: str | None
    created_at: str

    @classmethod
    def from_company(cls, company) -> "AdminCompanyResponse":
        return cls(
            id=company.id,
            name=company.name,
            slug=company.slug,
            company_type=company.company_type.value if company.company_type else "",
            verification_status=company.verification_status.value if company.verification_status else "",
            is_active=company.is_active,
            governorate=company.governorate,
            created_at=company.created_at.isoformat(),
        )


class AdminCompanyListResponse(BaseModel):
    items: list[AdminCompanyResponse]
    total: int
    page: int
    page_size: int


class AdminActionLogResponse(BaseModel):
    id: str
    admin_id: str
    action_type: AdminActionType
    target_type: str
    target_id: str
    details: dict | None
    created_at: str

    @classmethod
    def from_log(cls, log) -> "AdminActionLogResponse":
        return cls(
            id=log.id,
            admin_id=log.admin_id,
            action_type=log.action_type,
            target_type=log.target_type,
            target_id=log.target_id,
            details=log.details,
            created_at=log.created_at.isoformat(),
        )


class AdminActionLogListResponse(BaseModel):
    items: list[AdminActionLogResponse]
    total: int
    page: int
    page_size: int


class ShortlistAddRequest(BaseModel):
    company_id: str | None = None
    profile_id: str | None = None
    note: str | None = None


class ShortlistResponse(BaseModel):
    id: str
    company_id: str | None
    profile_id: str | None
    note: str | None
    created_at: str

    @classmethod
    def from_shortlist(cls, item) -> "ShortlistResponse":
        return cls(
            id=item.id,
            company_id=item.company_id,
            profile_id=item.profile_id,
            note=item.note,
            created_at=item.created_at.isoformat(),
        )


class ShortlistListResponse(BaseModel):
    items: list[ShortlistResponse]
    total: int
    page: int
    page_size: int
