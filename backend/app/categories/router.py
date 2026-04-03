from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import AdminUser
from app.categories.repository import CategoryRepository
from app.categories.schemas import (
    CategoryCreateRequest,
    CategoryResponse,
    CategoryUpdateRequest,
    GovernorateResponse,
)
from app.categories.service import CategoryService
from app.dependencies import get_db

router = APIRouter()


def _get_service(db: Annotated[AsyncSession, Depends(get_db)]) -> CategoryService:
    return CategoryService(CategoryRepository(db))


@router.get("/products", response_model=list[CategoryResponse])
async def list_product_categories(
    service: Annotated[CategoryService, Depends(_get_service)],
):
    cats = await service.list_product_categories()
    return cats


@router.get("/services", response_model=list[CategoryResponse])
async def list_service_categories(
    service: Annotated[CategoryService, Depends(_get_service)],
):
    cats = await service.list_service_categories()
    return cats


@router.get("/governorates", response_model=list[GovernorateResponse])
async def list_governorates(
    service: Annotated[CategoryService, Depends(_get_service)],
):
    return await service.list_governorates()


@router.post("/products", response_model=CategoryResponse, status_code=201)
async def create_product_category(
    body: CategoryCreateRequest,
    admin: AdminUser,
    service: Annotated[CategoryService, Depends(_get_service)],
):
    cat = await service.create_product_category(**body.model_dump())
    return cat


@router.post("/services", response_model=CategoryResponse, status_code=201)
async def create_service_category(
    body: CategoryCreateRequest,
    admin: AdminUser,
    service: Annotated[CategoryService, Depends(_get_service)],
):
    cat = await service.create_service_category(**body.model_dump())
    return cat


@router.patch("/products/{cat_id}", response_model=CategoryResponse)
async def update_product_category(
    cat_id: str,
    body: CategoryUpdateRequest,
    admin: AdminUser,
    service: Annotated[CategoryService, Depends(_get_service)],
):
    cat = await service.update_product_category(cat_id, **body.model_dump(exclude_unset=True))
    return cat


@router.patch("/services/{cat_id}", response_model=CategoryResponse)
async def update_service_category(
    cat_id: str,
    body: CategoryUpdateRequest,
    admin: AdminUser,
    service: Annotated[CategoryService, Depends(_get_service)],
):
    cat = await service.update_service_category(cat_id, **body.model_dump(exclude_unset=True))
    return cat
