from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import AdminUser, CurrentUser
from app.dependencies import get_db
from app.reviews.repository import ReviewRepository
from app.reviews.schemas import (
    ReviewCreateRequest,
    ReviewFlagRequest,
    ReviewFlagResponse,
    ReviewListResponse,
    ReviewResponse,
    ReviewUpdateRequest,
)
from app.reviews.service import ReviewService

router = APIRouter()


def _get_service(db: Annotated[AsyncSession, Depends(get_db)]) -> ReviewService:
    return ReviewService(ReviewRepository(db))


@router.post("/", response_model=ReviewResponse, status_code=201)
async def create_review(
    body: ReviewCreateRequest,
    user: CurrentUser,
    service: Annotated[ReviewService, Depends(_get_service)],
):
    review = await service.create_review(user, **body.model_dump(exclude_unset=True))
    return ReviewResponse.from_review(review)


@router.get("/company/{company_id}", response_model=ReviewListResponse)
async def list_company_reviews(
    company_id: str,
    service: Annotated[ReviewService, Depends(_get_service)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    items, total, avg = await service.list_reviews_for_company(company_id, page, page_size)
    return ReviewListResponse(
        items=[ReviewResponse.from_review(r) for r in items],
        total=total,
        page=page,
        page_size=page_size,
        average_rating=avg,
    )


@router.get("/profile/{profile_id}", response_model=ReviewListResponse)
async def list_profile_reviews(
    profile_id: str,
    service: Annotated[ReviewService, Depends(_get_service)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    items, total = await service.list_reviews_for_profile(profile_id, page, page_size)
    return ReviewListResponse(
        items=[ReviewResponse.from_review(r) for r in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/my", response_model=ReviewListResponse)
async def list_my_reviews(
    user: CurrentUser,
    service: Annotated[ReviewService, Depends(_get_service)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    items, total = await service.list_my_reviews(user, page, page_size)
    return ReviewListResponse(
        items=[ReviewResponse.from_review(r) for r in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.patch("/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: str,
    body: ReviewUpdateRequest,
    user: CurrentUser,
    service: Annotated[ReviewService, Depends(_get_service)],
):
    review = await service.update_review(review_id, user, **body.model_dump(exclude_unset=True))
    return ReviewResponse.from_review(review)


@router.post("/{review_id}/flag", response_model=ReviewFlagResponse, status_code=201)
async def flag_review(
    review_id: str,
    body: ReviewFlagRequest,
    user: CurrentUser,
    service: Annotated[ReviewService, Depends(_get_service)],
):
    flag = await service.flag_review(review_id, user, body.reason)
    return ReviewFlagResponse.from_flag(flag)


@router.post("/{review_id}/hide", response_model=ReviewResponse)
async def hide_review(
    review_id: str,
    user: AdminUser,
    service: Annotated[ReviewService, Depends(_get_service)],
):
    review = await service.hide_review(review_id, user)
    return ReviewResponse.from_review(review)
