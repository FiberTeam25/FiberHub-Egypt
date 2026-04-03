from pydantic import BaseModel, EmailStr, Field

from app.models.user import AccountType


class UserUpdateRequest(BaseModel):
    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    phone: str | None = Field(None, max_length=20)


class UserPublicResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    account_type: AccountType
    avatar_url: str | None
    created_at: str

    model_config = {"from_attributes": True}

    @classmethod
    def from_user(cls, user) -> "UserPublicResponse":
        return cls(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            account_type=user.account_type,
            avatar_url=user.avatar_url,
            created_at=user.created_at.isoformat(),
        )


class UserDetailResponse(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    phone: str | None
    account_type: AccountType
    email_verified: bool
    avatar_url: str | None
    last_login_at: str | None
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}

    @classmethod
    def from_user(cls, user) -> "UserDetailResponse":
        return cls(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            account_type=user.account_type,
            email_verified=user.email_verified,
            avatar_url=user.avatar_url,
            last_login_at=user.last_login_at.isoformat() if user.last_login_at else None,
            created_at=user.created_at.isoformat(),
            updated_at=user.updated_at.isoformat(),
        )
