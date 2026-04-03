from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.review import Review, ReviewFlag


class ReviewRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, review: Review) -> Review:
        self.db.add(review)
        await self.db.flush()
        return review

    async def get_by_id(self, review_id: str) -> Review | None:
        result = await self.db.execute(
            select(Review)
            .options(selectinload(Review.reviewer), selectinload(Review.flags))
            .where(Review.id == review_id)
        )
        return result.scalar_one_or_none()

    async def list_for_company(
        self, company_id: str, page: int = 1, page_size: int = 20
    ) -> tuple[list[Review], int]:
        base_filter = (Review.target_company_id == company_id) & (Review.is_visible == True)
        query = (
            select(Review)
            .options(selectinload(Review.reviewer))
            .where(base_filter)
            .order_by(Review.created_at.desc())
        )
        count_query = select(func.count()).select_from(Review).where(base_filter)

        total = (await self.db.execute(count_query)).scalar_one()
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        return list(result.scalars().all()), total

    async def list_for_profile(
        self, profile_id: str, page: int = 1, page_size: int = 20
    ) -> tuple[list[Review], int]:
        base_filter = (Review.target_profile_id == profile_id) & (Review.is_visible == True)
        query = (
            select(Review)
            .options(selectinload(Review.reviewer))
            .where(base_filter)
            .order_by(Review.created_at.desc())
        )
        count_query = select(func.count()).select_from(Review).where(base_filter)

        total = (await self.db.execute(count_query)).scalar_one()
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        return list(result.scalars().all()), total

    async def list_by_reviewer(
        self, user_id: str, page: int = 1, page_size: int = 20
    ) -> tuple[list[Review], int]:
        query = (
            select(Review)
            .options(selectinload(Review.reviewer))
            .where(Review.reviewer_id == user_id)
            .order_by(Review.created_at.desc())
        )
        count_query = (
            select(func.count()).select_from(Review).where(Review.reviewer_id == user_id)
        )

        total = (await self.db.execute(count_query)).scalar_one()
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        return list(result.scalars().all()), total

    async def get_average_rating(self, company_id: str) -> float | None:
        result = await self.db.execute(
            select(func.avg(Review.overall_rating))
            .where(Review.target_company_id == company_id, Review.is_visible == True)
        )
        avg = result.scalar_one()
        return round(float(avg), 2) if avg else None

    async def has_reviewed(
        self, reviewer_id: str, target_company_id: str | None = None,
        target_profile_id: str | None = None,
    ) -> bool:
        query = select(func.count()).select_from(Review).where(Review.reviewer_id == reviewer_id)
        if target_company_id:
            query = query.where(Review.target_company_id == target_company_id)
        if target_profile_id:
            query = query.where(Review.target_profile_id == target_profile_id)
        result = await self.db.execute(query)
        return result.scalar_one() > 0

    async def create_flag(self, flag: ReviewFlag) -> ReviewFlag:
        self.db.add(flag)
        await self.db.flush()
        return flag

    async def list_flagged(
        self, page: int = 1, page_size: int = 20
    ) -> tuple[list[Review], int]:
        query = (
            select(Review)
            .options(selectinload(Review.reviewer), selectinload(Review.flags))
            .join(ReviewFlag)
            .where(ReviewFlag.resolved == False)
            .distinct()
            .order_by(Review.created_at.desc())
        )
        count_query = (
            select(func.count(func.distinct(Review.id)))
            .select_from(Review)
            .join(ReviewFlag)
            .where(ReviewFlag.resolved == False)
        )

        total = (await self.db.execute(count_query)).scalar_one()
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        return list(result.scalars().all()), total
