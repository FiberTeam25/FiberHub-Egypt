from slugify import slugify

from app.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.models.profile import IndividualProfile
from app.models.user import AccountType, User
from app.profiles.repository import ProfileRepository


class ProfileService:
    def __init__(self, repo: ProfileRepository):
        self.repo = repo

    async def create_profile(self, user: User, **kwargs) -> IndividualProfile:
        if user.account_type != AccountType.INDIVIDUAL:
            raise ForbiddenError("Only individual account types can create a professional profile")

        existing = await self.repo.get_by_user_id(user.id)
        if existing:
            raise ConflictError("You already have a professional profile")

        slug = await self._generate_unique_slug(user.full_name)
        profile = IndividualProfile(user_id=user.id, slug=slug, **kwargs)
        profile.profile_completion = self._calculate_completion(profile)
        profile = await self.repo.create(profile)
        return profile

    async def get_profile_by_slug(self, slug: str) -> IndividualProfile:
        profile = await self.repo.get_by_slug(slug)
        if not profile:
            raise NotFoundError("Profile not found")
        return profile

    async def get_profile_by_id(self, profile_id: str) -> IndividualProfile:
        profile = await self.repo.get_by_id(profile_id)
        if not profile:
            raise NotFoundError("Profile not found")
        return profile

    async def update_profile(
        self, profile_id: str, user: User, **kwargs
    ) -> IndividualProfile:
        profile = await self.get_profile_by_id(profile_id)
        if profile.user_id != user.id and not user.is_admin:
            raise ForbiddenError("You can only edit your own profile")

        for key, value in kwargs.items():
            if value is not None and hasattr(profile, key):
                setattr(profile, key, value)

        profile.profile_completion = self._calculate_completion(profile)
        await self.repo.db.flush()
        return profile

    async def list_profiles(self, **filters) -> tuple[list[IndividualProfile], int]:
        return await self.repo.list_profiles(**filters)

    async def _generate_unique_slug(self, name: str) -> str:
        base_slug = slugify(name, max_length=200)
        slug = base_slug
        counter = 1
        while await self.repo.slug_exists(slug):
            slug = f"{base_slug}-{counter}"
            counter += 1
        return slug

    @staticmethod
    def _calculate_completion(profile: IndividualProfile) -> int:
        fields = [
            profile.headline,
            profile.bio,
            profile.specializations,
            profile.experience_years,
            profile.city,
            profile.governorate,
            profile.availability,
        ]
        filled = sum(1 for f in fields if f)
        return int((filled / len(fields)) * 100)
