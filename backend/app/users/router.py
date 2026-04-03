from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.auth.schemas import UserResponse
from app.dependencies import get_db
from app.users.repository import UserRepository
from app.users.schemas import UserPublicResponse, UserUpdateRequest
from app.users.service import UserService

router = APIRouter()


def _get_service(db: Annotated[AsyncSession, Depends(get_db)]) -> UserService:
    return UserService(UserRepository(db))


@router.get("/{user_id}", response_model=UserPublicResponse)
async def get_user(
    user_id: str,
    service: Annotated[UserService, Depends(_get_service)],
):
    user = await service.get_user_public(user_id)
    return UserPublicResponse.from_user(user)


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    body: UserUpdateRequest,
    user: CurrentUser,
    service: Annotated[UserService, Depends(_get_service)],
):
    updated = await service.update_user(
        user,
        first_name=body.first_name,
        last_name=body.last_name,
        phone=body.phone,
    )
    return UserResponse.from_user(updated)
