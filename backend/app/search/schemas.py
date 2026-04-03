from pydantic import BaseModel, Field

from app.companies.schemas import CompanyResponse
from app.profiles.schemas import ProfileResponse


class SearchRequest(BaseModel):
    q: str | None = Field(None, max_length=200)
    company_type: str | None = None
    governorate: str | None = None
    category_id: str | None = None
    category_type: str | None = None  # 'product' or 'service'
    verified_only: bool = False
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class UnifiedSearchResponse(BaseModel):
    companies: list[CompanyResponse]
    companies_total: int
    profiles: list[ProfileResponse]
    profiles_total: int
    page: int
    page_size: int
