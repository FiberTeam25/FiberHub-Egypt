from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin.repository import AdminRepository
from app.admin.schemas import (
    AdminActionLogListResponse,
    AdminActionLogResponse,
    AdminCompanyListResponse,
    AdminCompanyResponse,
    AdminUserListResponse,
    AdminUserResponse,
    DashboardStatsResponse,
    ShortlistAddRequest,
    ShortlistListResponse,
    ShortlistResponse,
)
from app.admin.service import AdminService
from app.auth.dependencies import AdminUser, CurrentUser
from app.dependencies import get_db

router = APIRouter()


def _get_service(db: Annotated[AsyncSession, Depends(get_db)]) -> AdminService:
    return AdminService(AdminRepository(db))


# --- Admin-only endpoints ---


@router.get("/dashboard", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    user: AdminUser,
    service: Annotated[AdminService, Depends(_get_service)],
):
    stats = await service.get_dashboard_stats()
    return DashboardStatsResponse(**stats)


@router.get("/users", response_model=AdminUserListResponse)
async def list_users(
    user: AdminUser,
    service: Annotated[AdminService, Depends(_get_service)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = None,
    search: str | None = None,
):
    items, total = await service.list_users(page, page_size, status, search)
    return AdminUserListResponse(
        items=[AdminUserResponse.from_user(u) for u in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/users/{user_id}/suspend", response_model=AdminUserResponse)
async def suspend_user(
    user_id: str,
    user: AdminUser,
    service: Annotated[AdminService, Depends(_get_service)],
):
    suspended = await service.suspend_user(user_id, user)
    return AdminUserResponse.from_user(suspended)


@router.post("/users/{user_id}/activate", response_model=AdminUserResponse)
async def activate_user(
    user_id: str,
    user: AdminUser,
    service: Annotated[AdminService, Depends(_get_service)],
):
    activated = await service.activate_user(user_id, user)
    return AdminUserResponse.from_user(activated)


@router.get("/companies", response_model=AdminCompanyListResponse)
async def list_companies(
    user: AdminUser,
    service: Annotated[AdminService, Depends(_get_service)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    verification_status: str | None = None,
    search: str | None = None,
):
    items, total = await service.list_companies(
        page, page_size, verification_status, search,
    )
    return AdminCompanyListResponse(
        items=[AdminCompanyResponse.from_company(c) for c in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/action-logs", response_model=AdminActionLogListResponse)
async def list_action_logs(
    user: AdminUser,
    service: Annotated[AdminService, Depends(_get_service)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    admin_id: str | None = None,
):
    items, total = await service.list_action_logs(page, page_size, admin_id)
    return AdminActionLogListResponse(
        items=[AdminActionLogResponse.from_log(log) for log in items],
        total=total,
        page=page,
        page_size=page_size,
    )


# --- Shortlist endpoints (any authenticated user) ---


@router.get("/shortlist", response_model=ShortlistListResponse)
async def list_shortlist(
    user: CurrentUser,
    service: Annotated[AdminService, Depends(_get_service)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    items, total = await service.list_shortlist(user, page, page_size)
    return ShortlistListResponse(
        items=[ShortlistResponse.from_shortlist(s) for s in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/shortlist", response_model=ShortlistResponse, status_code=201)
async def add_to_shortlist(
    body: ShortlistAddRequest,
    user: CurrentUser,
    service: Annotated[AdminService, Depends(_get_service)],
):
    item = await service.add_to_shortlist(
        user, company_id=body.company_id, profile_id=body.profile_id, note=body.note,
    )
    return ShortlistResponse.from_shortlist(item)


@router.delete("/shortlist/{shortlist_id}")
async def remove_from_shortlist(
    shortlist_id: str,
    user: CurrentUser,
    service: Annotated[AdminService, Depends(_get_service)],
):
    await service.remove_from_shortlist(shortlist_id, user)
    return {"message": "Removed from shortlist"}
