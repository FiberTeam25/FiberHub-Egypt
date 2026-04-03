from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.dependencies import get_db
from app.profiles.repository import ProfileRepository
from app.profiles.schemas import ProfileCreateRequest, ProfileListResponse, ProfileResponse, ProfileUpdateRequest
from app.profiles.service import ProfileService

router = APIRouter()


def _get_service(db: Annotated[AsyncSession, Depends(get_db)]) -> ProfileService:
    return ProfileService(ProfileRepository(db))


@router.post("/", response_model=ProfileResponse, status_code=201)
async def create_profile(
    body: ProfileCreateRequest,
    user: CurrentUser,
    service: Annotated[ProfileService, Depends(_get_service)],
):
    profile = await service.create_profile(user, **body.model_dump(exclude_unset=True))
    return ProfileResponse.from_profile(profile)


@router.get("/", response_model=ProfileListResponse)
async def list_profiles(
    service: Annotated[ProfileService, Depends(_get_service)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    governorate: str | None = None,
    specialization: str | None = None,
    verified_only: bool = False,
    search: str | None = None,
):
    items, total = await service.list_profiles(
        page=page,
        page_size=page_size,
        governorate=governorate,
        specialization=specialization,
        verified_only=verified_only,
        search=search,
    )
    return ProfileListResponse(
        items=[ProfileResponse.from_profile(p) for p in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{slug}", response_model=ProfileResponse)
async def get_profile(
    slug: str,
    service: Annotated[ProfileService, Depends(_get_service)],
):
    profile = await service.get_profile_by_slug(slug)
    return ProfileResponse.from_profile(profile)


@router.patch("/{profile_id}", response_model=ProfileResponse)
async def update_profile(
    profile_id: str,
    body: ProfileUpdateRequest,
    user: CurrentUser,
    service: Annotated[ProfileService, Depends(_get_service)],
):
    profile = await service.update_profile(
        profile_id, user, **body.model_dump(exclude_unset=True)
    )
    return ProfileResponse.from_profile(profile)
