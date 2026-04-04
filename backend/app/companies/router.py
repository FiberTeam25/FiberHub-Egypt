from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.auth.schemas import MessageResponse
from app.companies.repository import CompanyRepository
from app.exceptions import NotFoundError
from app.companies.schemas import (
    CertificationRequest,
    CompanyCreateRequest,
    CompanyListResponse,
    CompanyProductRequest,
    CompanyResponse,
    CompanyServiceRequest,
    CompanyUpdateRequest,
    MemberAddRequest,
    MemberResponse,
    MemberUpdateRequest,
    ProjectReferenceRequest,
)
from app.companies.service import CompanyService
from app.dependencies import get_db
from app.users.repository import UserRepository

router = APIRouter()


def _get_service(db: Annotated[AsyncSession, Depends(get_db)]) -> CompanyService:
    return CompanyService(CompanyRepository(db))


def _get_user_repo(db: Annotated[AsyncSession, Depends(get_db)]) -> UserRepository:
    return UserRepository(db)


# --- Company CRUD ---

@router.post("/", response_model=CompanyResponse, status_code=201)
async def create_company(
    body: CompanyCreateRequest,
    user: CurrentUser,
    service: Annotated[CompanyService, Depends(_get_service)],
):
    company = await service.create_company(user, **body.model_dump())
    return CompanyResponse.from_company(company)


@router.get("/", response_model=CompanyListResponse)
async def list_companies(
    service: Annotated[CompanyService, Depends(_get_service)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    company_type: str | None = None,
    governorate: str | None = None,
    verified_only: bool = False,
    search: str | None = None,
):
    items, total = await service.list_companies(
        page=page,
        page_size=page_size,
        company_type=company_type,
        governorate=governorate,
        verified_only=verified_only,
        search=search,
    )
    return CompanyListResponse(
        items=[CompanyResponse.from_company(c) for c in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/mine", response_model=CompanyResponse | None)
async def get_my_company(
    user: CurrentUser,
    service: Annotated[CompanyService, Depends(_get_service)],
):
    company = await service.get_primary_company(user)
    if not company:
        return None
    return CompanyResponse.from_company(company)


@router.get("/{slug}", response_model=CompanyResponse)
async def get_company(
    slug: str,
    service: Annotated[CompanyService, Depends(_get_service)],
):
    company = await service.get_company_by_slug(slug)
    return CompanyResponse.from_company(company)


@router.patch("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: str,
    body: CompanyUpdateRequest,
    user: CurrentUser,
    service: Annotated[CompanyService, Depends(_get_service)],
):
    company = await service.update_company(
        company_id, user, **body.model_dump(exclude_unset=True)
    )
    return CompanyResponse.from_company(company)


# --- Members ---

@router.get("/{company_id}/members", response_model=list[MemberResponse])
async def list_members(
    company_id: str,
    service: Annotated[CompanyService, Depends(_get_service)],
):
    members = await service.list_members(company_id)
    return [MemberResponse.from_member(m) for m in members]


@router.post("/{company_id}/members", response_model=MemberResponse, status_code=201)
async def add_member(
    company_id: str,
    body: MemberAddRequest,
    user: CurrentUser,
    service: Annotated[CompanyService, Depends(_get_service)],
    user_repo: Annotated[UserRepository, Depends(_get_user_repo)],
):
    target_user = await user_repo.get_by_email(body.email)
    if not target_user:
        raise NotFoundError("User with this email not found")

    member = await service.add_member(
        company_id, user, target_user, body.role, body.title
    )
    # Reload to get user relationship populated
    repo = CompanyRepository(user_repo.db)
    member = await repo.get_member_by_id(member.id)
    return MemberResponse.from_member(member)


@router.patch("/{company_id}/members/{member_id}", response_model=MemberResponse)
async def update_member(
    company_id: str,
    member_id: str,
    body: MemberUpdateRequest,
    user: CurrentUser,
    service: Annotated[CompanyService, Depends(_get_service)],
):
    member = await service.update_member(
        company_id, member_id, user, **body.model_dump(exclude_unset=True)
    )
    return MemberResponse.from_member(member)


@router.delete("/{company_id}/members/{member_id}", response_model=MessageResponse)
async def remove_member(
    company_id: str,
    member_id: str,
    user: CurrentUser,
    service: Annotated[CompanyService, Depends(_get_service)],
):
    await service.remove_member(company_id, member_id, user)
    return MessageResponse(message="Member removed")


# --- Services ---

@router.post("/{company_id}/services", response_model=MessageResponse, status_code=201)
async def add_service(
    company_id: str,
    body: CompanyServiceRequest,
    user: CurrentUser,
    service: Annotated[CompanyService, Depends(_get_service)],
):
    await service.add_service(company_id, user, body.service_category_id, body.description)
    return MessageResponse(message="Service added")


@router.delete("/{company_id}/services/{service_id}", response_model=MessageResponse)
async def remove_service(
    company_id: str,
    service_id: str,
    user: CurrentUser,
    service: Annotated[CompanyService, Depends(_get_service)],
):
    await service.remove_service(company_id, service_id, user)
    return MessageResponse(message="Service removed")


# --- Products ---

@router.post("/{company_id}/products", response_model=MessageResponse, status_code=201)
async def add_product(
    company_id: str,
    body: CompanyProductRequest,
    user: CurrentUser,
    service: Annotated[CompanyService, Depends(_get_service)],
):
    await service.add_product(
        company_id, user, body.product_category_id, body.brand_names, body.description
    )
    return MessageResponse(message="Product added")


@router.delete("/{company_id}/products/{product_id}", response_model=MessageResponse)
async def remove_product(
    company_id: str,
    product_id: str,
    user: CurrentUser,
    service: Annotated[CompanyService, Depends(_get_service)],
):
    await service.remove_product(company_id, product_id, user)
    return MessageResponse(message="Product removed")


# --- Certifications ---

@router.post("/{company_id}/certifications", response_model=MessageResponse, status_code=201)
async def add_certification(
    company_id: str,
    body: CertificationRequest,
    user: CurrentUser,
    service: Annotated[CompanyService, Depends(_get_service)],
):
    await service.add_certification(company_id, user, **body.model_dump())
    return MessageResponse(message="Certification added")


@router.delete("/{company_id}/certifications/{cert_id}", response_model=MessageResponse)
async def remove_certification(
    company_id: str,
    cert_id: str,
    user: CurrentUser,
    service: Annotated[CompanyService, Depends(_get_service)],
):
    await service.remove_certification(company_id, cert_id, user)
    return MessageResponse(message="Certification removed")


# --- References ---

@router.post("/{company_id}/references", response_model=MessageResponse, status_code=201)
async def add_reference(
    company_id: str,
    body: ProjectReferenceRequest,
    user: CurrentUser,
    service: Annotated[CompanyService, Depends(_get_service)],
):
    await service.add_reference(company_id, user, **body.model_dump())
    return MessageResponse(message="Reference added")


@router.delete("/{company_id}/references/{ref_id}", response_model=MessageResponse)
async def remove_reference(
    company_id: str,
    ref_id: str,
    user: CurrentUser,
    service: Annotated[CompanyService, Depends(_get_service)],
):
    await service.remove_reference(company_id, ref_id, user)
    return MessageResponse(message="Reference removed")
