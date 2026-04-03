from pydantic import BaseModel, EmailStr, Field

from app.models.user import AccountType


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    phone: str | None = Field(None, max_length=20)
    account_type: AccountType


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class VerifyEmailRequest(BaseModel):
    token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


class UserResponse(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    phone: str | None
    account_type: AccountType
    email_verified: bool
    avatar_url: str | None
    created_at: str

    model_config = {"from_attributes": True}

    @classmethod
    def from_user(cls, user) -> "UserResponse":
        return cls(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            account_type=user.account_type,
            email_verified=user.email_verified,
            avatar_url=user.avatar_url,
            created_at=user.created_at.isoformat(),
        )


class MessageResponse(BaseModel):
    message: str
