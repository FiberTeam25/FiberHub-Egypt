from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.company import Company, CompanyService as CompanyServiceModel, CompanyProduct
from app.models.profile import IndividualProfile


class SearchService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def search_companies(
        self,
        q: str | None = None,
        company_type: str | None = None,
        governorate: str | None = None,
        category_id: str | None = None,
        category_type: str | None = None,
        verified_only: bool = False,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Company], int]:
        query = select(Company).where(Company.is_active.is_(True))
        count_query = select(func.count()).select_from(Company).where(Company.is_active.is_(True))

        if q:
            # Use PostgreSQL full-text search via ilike as fallback
            # tsvector index will accelerate this on large datasets
            search_filter = or_(
                Company.name.ilike(f"%{q}%"),
                Company.description.ilike(f"%{q}%"),
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        if company_type:
            query = query.where(Company.company_type == company_type)
            count_query = count_query.where(Company.company_type == company_type)

        if governorate:
            query = query.where(Company.governorate == governorate)
            count_query = count_query.where(Company.governorate == governorate)

        if verified_only:
            query = query.where(Company.verification_status == "approved")
            count_query = count_query.where(Company.verification_status == "approved")

        if category_id and category_type:
            if category_type == "service":
                subq = (
                    select(CompanyServiceModel.company_id)
                    .where(CompanyServiceModel.service_category_id == category_id)
                )
            else:
                subq = (
                    select(CompanyProduct.company_id)
                    .where(CompanyProduct.product_category_id == category_id)
                )
            query = query.where(Company.id.in_(subq))
            count_query = count_query.where(Company.id.in_(subq))

        total = (await self.db.execute(count_query)).scalar_one()

        query = query.order_by(Company.verification_status.desc(), Company.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)

        return list(result.scalars().all()), total

    async def search_profiles(
        self,
        q: str | None = None,
        governorate: str | None = None,
        specialization: str | None = None,
        verified_only: bool = False,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[IndividualProfile], int]:
        query = select(IndividualProfile).options(selectinload(IndividualProfile.user))
        count_query = select(func.count()).select_from(IndividualProfile)

        if q:
            search_filter = or_(
                IndividualProfile.headline.ilike(f"%{q}%"),
                IndividualProfile.bio.ilike(f"%{q}%"),
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

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

        total = (await self.db.execute(count_query)).scalar_one()

        query = query.order_by(IndividualProfile.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)

        return list(result.scalars().all()), total
