from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.company import VerificationStatusEnum
from app.models.verification import VerificationDocument, VerificationRequest


class VerificationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, request: VerificationRequest) -> VerificationRequest:
        self.db.add(request)
        await self.db.flush()
        return request

    async def add_document(self, doc: VerificationDocument) -> VerificationDocument:
        self.db.add(doc)
        await self.db.flush()
        return doc

    async def get_by_id(self, request_id: str) -> VerificationRequest | None:
        result = await self.db.execute(
            select(VerificationRequest)
            .options(selectinload(VerificationRequest.documents))
            .where(VerificationRequest.id == request_id)
        )
        return result.scalar_one_or_none()

    async def get_latest_for_company(self, company_id: str) -> VerificationRequest | None:
        result = await self.db.execute(
            select(VerificationRequest)
            .options(selectinload(VerificationRequest.documents))
            .where(VerificationRequest.company_id == company_id)
            .order_by(VerificationRequest.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_latest_for_profile(self, profile_id: str) -> VerificationRequest | None:
        result = await self.db.execute(
            select(VerificationRequest)
            .options(selectinload(VerificationRequest.documents))
            .where(VerificationRequest.profile_id == profile_id)
            .order_by(VerificationRequest.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def list_pending(
        self, page: int = 1, page_size: int = 20, status: str | None = None,
    ) -> tuple[list[VerificationRequest], int]:
        query = select(VerificationRequest).options(
            selectinload(VerificationRequest.documents)
        )
        count_query = select(func.count()).select_from(VerificationRequest)

        if status:
            query = query.where(VerificationRequest.status == status)
            count_query = count_query.where(VerificationRequest.status == status)
        else:
            query = query.where(
                VerificationRequest.status == VerificationStatusEnum.PENDING
            )
            count_query = count_query.where(
                VerificationRequest.status == VerificationStatusEnum.PENDING
            )

        total = (await self.db.execute(count_query)).scalar_one()

        query = query.order_by(VerificationRequest.submitted_at.asc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)

        return list(result.scalars().all()), total
