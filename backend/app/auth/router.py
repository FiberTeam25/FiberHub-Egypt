from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.auth.schemas import (
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserResponse,
    VerifyEmailRequest,
)
from app.auth.service import AuthService
from app.dependencies import get_db

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    body: RegisterRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = AuthService(db)
    user, verification_token = await service.register(
        email=body.email,
        password=body.password,
        first_name=body.first_name,
        last_name=body.last_name,
        phone=body.phone,
        account_type=body.account_type,
    )
    # Send verification email (direct async call; swap to arq queue post-MVP)
    try:
        from app.workers.email import send_verification_email
        await send_verification_email(user.email, verification_token)
    except Exception:
        import logging
        logging.getLogger(__name__).warning("Failed to send verification email to %s", user.email)
    return UserResponse.from_user(user)


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = AuthService(db)
    access_token, refresh_token, user = await service.login(
        email=body.email,
        password=body.password,
    )
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    body: RefreshRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = AuthService(db)
    access_token, new_refresh = await service.refresh_access_token(body.refresh_token)
    return TokenResponse(access_token=access_token, refresh_token=new_refresh)


@router.post("/logout", response_model=MessageResponse)
async def logout(
    body: RefreshRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = AuthService(db)
    await service.logout(body.refresh_token)
    return MessageResponse(message="Logged out successfully")


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(
    body: VerifyEmailRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = AuthService(db)
    await service.verify_email(body.token)
    return MessageResponse(message="Email verified successfully")


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    body: ForgotPasswordRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = AuthService(db)
    token = await service.create_password_reset_token(body.email)
    if token:
        try:
            from app.workers.email import send_password_reset_email
            await send_password_reset_email(body.email, token)
        except Exception:
            import logging
            logging.getLogger(__name__).warning("Failed to send reset email to %s", body.email)
    return MessageResponse(message="If an account exists with this email, a reset link has been sent")


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    body: ResetPasswordRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = AuthService(db)
    await service.reset_password(body.token, body.new_password)
    return MessageResponse(message="Password reset successfully")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(user: CurrentUser):
    return UserResponse.from_user(user)
