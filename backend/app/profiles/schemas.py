from pydantic import BaseModel, Field

from app.models.company import VerificationStatusEnum


class ProfileCreateRequest(BaseModel):
    headline: str | None = Field(None, max_length=255)
    bio: str | None = None
    specializations: list[str] | None = None
    experience_years: int | None = Field(None, ge=0)
    city: str | None = Field(None, max_length=100)
    governorate: str | None = Field(None, max_length=100)
    availability: str | None = Field(None, max_length=50)
    hourly_rate_egp: float | None = Field(None, ge=0)


class ProfileUpdateRequest(BaseModel):
    headline: str | None = Field(None, max_length=255)
    bio: str | None = None
    specializations: list[str] | None = None
    experience_years: int | None = Field(None, ge=0)
    city: str | None = Field(None, max_length=100)
    governorate: str | None = Field(None, max_length=100)
    availability: str | None = Field(None, max_length=50)
    hourly_rate_egp: float | None = Field(None, ge=0)


class ProfileResponse(BaseModel):
    id: str
    user_id: str
    slug: str
    headline: str | None
    bio: str | None
    specializations: list[str] | None
    experience_years: int | None
    city: str | None
    governorate: str | None
    availability: str | None
    hourly_rate_egp: float | None
    resume_url: str | None
    verification_status: VerificationStatusEnum
    profile_completion: int
    created_at: str
    # Include user name for display
    first_name: str | None = None
    last_name: str | None = None
    avatar_url: str | None = None

    @classmethod
    def from_profile(cls, profile) -> "ProfileResponse":
        user = profile.user
        return cls(
            id=profile.id,
            user_id=profile.user_id,
            slug=profile.slug,
            headline=profile.headline,
            bio=profile.bio,
            specializations=profile.specializations,
            experience_years=profile.experience_years,
            city=profile.city,
            governorate=profile.governorate,
            availability=profile.availability,
            hourly_rate_egp=float(profile.hourly_rate_egp) if profile.hourly_rate_egp else None,
            resume_url=profile.resume_url,
            verification_status=profile.verification_status,
            profile_completion=profile.profile_completion,
            created_at=profile.created_at.isoformat(),
            first_name=user.first_name if user else None,
            last_name=user.last_name if user else None,
            avatar_url=user.avatar_url if user else None,
        )


class ProfileListResponse(BaseModel):
    items: list[ProfileResponse]
    total: int
    page: int
    page_size: int
