from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.companies.schemas import CompanyListResponse, CompanyResponse
from app.dependencies import get_db
from app.profiles.schemas import ProfileListResponse, ProfileResponse
from app.search.schemas import UnifiedSearchResponse
from app.search.service import SearchService

router = APIRouter()


def _get_service(db: Annotated[AsyncSession, Depends(get_db)]) -> SearchService:
    return SearchService(db)


@router.get("/", response_model=UnifiedSearchResponse)
async def unified_search(
    service: Annotated[SearchService, Depends(_get_service)],
    q: str | None = None,
    company_type: str | None = None,
    governorate: str | None = None,
    category_id: str | None = None,
    category_type: str | None = None,
    verified_only: bool = False,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
):
    companies, companies_total = await service.search_companies(
        q=q, company_type=company_type, governorate=governorate,
        category_id=category_id, category_type=category_type,
        verified_only=verified_only, page=page, page_size=page_size,
    )
    profiles, profiles_total = await service.search_profiles(
        q=q, governorate=governorate, verified_only=verified_only,
        page=page, page_size=page_size,
    )
    return UnifiedSearchResponse(
        companies=[CompanyResponse.from_company(c) for c in companies],
        companies_total=companies_total,
        profiles=[ProfileResponse.from_profile(p) for p in profiles],
        profiles_total=profiles_total,
        page=page,
        page_size=page_size,
    )


@router.get("/companies", response_model=CompanyListResponse)
async def search_companies(
    service: Annotated[SearchService, Depends(_get_service)],
    q: str | None = None,
    company_type: str | None = None,
    governorate: str | None = None,
    category_id: str | None = None,
    category_type: str | None = None,
    verified_only: bool = False,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    items, total = await service.search_companies(
        q=q, company_type=company_type, governorate=governorate,
        category_id=category_id, category_type=category_type,
        verified_only=verified_only, page=page, page_size=page_size,
    )
    return CompanyListResponse(
        items=[CompanyResponse.from_company(c) for c in items],
        total=total, page=page, page_size=page_size,
    )


@router.get("/profiles", response_model=ProfileListResponse)
async def search_profiles(
    service: Annotated[SearchService, Depends(_get_service)],
    q: str | None = None,
    governorate: str | None = None,
    specialization: str | None = None,
    verified_only: bool = False,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    items, total = await service.search_profiles(
        q=q, governorate=governorate, specialization=specialization,
        verified_only=verified_only, page=page, page_size=page_size,
    )
    return ProfileListResponse(
        items=[ProfileResponse.from_profile(p) for p in items],
        total=total, page=page, page_size=page_size,
    )
