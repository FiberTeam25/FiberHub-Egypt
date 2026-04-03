from app.exceptions import BadRequestError, ConflictError, ForbiddenError, NotFoundError
from app.models.review import Review, ReviewFlag, ReviewTargetType
from app.models.user import User
from app.reviews.repository import ReviewRepository


class ReviewService:
    def __init__(self, repo: ReviewRepository):
        self.repo = repo

    async def create_review(self, user: User, **kwargs) -> Review:
        target_type = kwargs.get("target_type")
        target_company_id = kwargs.get("target_company_id")
        target_profile_id = kwargs.get("target_profile_id")

        if target_type == ReviewTargetType.COMPANY and not target_company_id:
            raise BadRequestError("target_company_id is required for company reviews")
        if target_type == ReviewTargetType.INDIVIDUAL and not target_profile_id:
            raise BadRequestError("target_profile_id is required for individual reviews")

        # Prevent duplicate reviews for same target
        if await self.repo.has_reviewed(
            user.id,
            target_company_id=target_company_id,
            target_profile_id=target_profile_id,
        ):
            raise ConflictError("You have already reviewed this entity")

        review = Review(reviewer_id=user.id, **kwargs)
        return await self.repo.create(review)

    async def list_reviews_for_company(
        self, company_id: str, page: int = 1, page_size: int = 20
    ) -> tuple[list[Review], int, float | None]:
        items, total = await self.repo.list_for_company(company_id, page, page_size)
        avg = await self.repo.get_average_rating(company_id)
        return items, total, avg

    async def list_reviews_for_profile(
        self, profile_id: str, page: int = 1, page_size: int = 20
    ) -> tuple[list[Review], int]:
        return await self.repo.list_for_profile(profile_id, page, page_size)

    async def list_my_reviews(
        self, user: User, page: int = 1, page_size: int = 20
    ) -> tuple[list[Review], int]:
        return await self.repo.list_by_reviewer(user.id, page, page_size)

    async def update_review(self, review_id: str, user: User, **kwargs) -> Review:
        review = await self.repo.get_by_id(review_id)
        if not review:
            raise NotFoundError("Review not found")
        if review.reviewer_id != user.id:
            raise ForbiddenError("You can only edit your own reviews")

        for key, value in kwargs.items():
            if value is not None and hasattr(review, key):
                setattr(review, key, value)
        await self.repo.db.flush()
        return review

    async def flag_review(self, review_id: str, user: User, reason: str) -> ReviewFlag:
        review = await self.repo.get_by_id(review_id)
        if not review:
            raise NotFoundError("Review not found")

        flag = ReviewFlag(
            review_id=review_id,
            flagged_by=user.id,
            reason=reason,
        )
        return await self.repo.create_flag(flag)

    async def hide_review(self, review_id: str, admin_user: User) -> Review:
        review = await self.repo.get_by_id(review_id)
        if not review:
            raise NotFoundError("Review not found")
        review.is_visible = False
        await self.repo.db.flush()
        return review

    async def list_flagged(
        self, page: int = 1, page_size: int = 20
    ) -> tuple[list[Review], int]:
        return await self.repo.list_flagged(page, page_size)
