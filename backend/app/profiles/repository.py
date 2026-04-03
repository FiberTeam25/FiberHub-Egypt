from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.profile import IndividualProfile


class ProfileRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, profile: IndividualProfile) -> IndividualProfile:
        self.db.add(profile)
        await self.db.flush()
        return profile

    async def get_by_id(self, profile_id: str) -> IndividualProfile | None:
        result = await self.db.execute(
            select(IndividualProfile)
            .options(selectinload(IndividualProfile.user))
            .where(IndividualProfile.id == profile_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: str) -> IndividualProfile | None:
        result = await self.db.execute(
            select(IndividualProfile)
            .options(selectinload(IndividualProfile.user))
            .where(IndividualProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> IndividualProfile | None:
        result = await self.db.execute(
            select(IndividualProfile)
            .options(selectinload(IndividualProfile.user))
            .where(IndividualProfile.slug == slug)
        )
        return result.scalar_one_or_none()

    async def slug_exists(self, slug: str) -> bool:
        result = await self.db.execute(
            select(func.count())
            .select_from(IndividualProfile)
            .where(IndividualProfile.slug == slug)
        )
        return result.scalar_one() > 0

    async def list_profiles(
        self,
        page: int = 1,
        page_size: int = 20,
        governorate: str | None = None,
        specialization: str | None = None,
        verified_only: bool = False,
        search: str | None = None,
    ) -> tuple[list[IndividualProfile], int]:
        query = select(IndividualProfile).options(selectinload(IndividualProfile.user))
        count_query = select(func.count()).select_from(IndividualProfile)

        if governorate:
            query = query.where(IndividualProfile.governorate == governorate)
            count_query = count_query.where(IndividualProfile.governorate == governorate)

        if specialization:
            query = query.where(IndividualProfile.specializations.any(specialization))
            count_query = count_query.where(
                IndividualProfile.specializations.any(specialization)
            )

        if verified_only:
            query = query.where(IndividualProfile.verification_status == "approved")
            count_query = count_query.where(
                IndividualProfile.verification_status == "approved"
            )

        if search:
            search_filter = IndividualProfile.headline.ilike(f"%{search}%")
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        total = (await self.db.execute(count_query)).scalar_one()

        query = query.order_by(IndividualProfile.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)

        return list(result.scalars().all()), total
