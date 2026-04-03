from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.rfq import (
    RFQ,
    RFQAttachment,
    RFQInvitation,
    RFQResponse,
    RFQStatus,
    RFQStatusHistory,
)


class RFQRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, rfq: RFQ) -> RFQ:
        self.db.add(rfq)
        await self.db.flush()
        return rfq

    async def get_by_id(self, rfq_id: str) -> RFQ | None:
        result = await self.db.execute(
            select(RFQ)
            .options(
                selectinload(RFQ.buyer_company),
                selectinload(RFQ.attachments),
                selectinload(RFQ.invitations).selectinload(RFQInvitation.company),
            )
            .where(RFQ.id == rfq_id)
        )
        return result.scalar_one_or_none()

    async def list_by_buyer(
        self, company_id: str, page: int = 1, page_size: int = 20,
        status: str | None = None,
    ) -> tuple[list[RFQ], int]:
        query = (
            select(RFQ)
            .options(
                selectinload(RFQ.buyer_company),
                selectinload(RFQ.invitations),
            )
            .where(RFQ.company_id == company_id)
        )
        count_query = (
            select(func.count()).select_from(RFQ)
            .where(RFQ.company_id == company_id)
        )

        if status:
            query = query.where(RFQ.status == status)
            count_query = count_query.where(RFQ.status == status)

        total = (await self.db.execute(count_query)).scalar_one()
        query = query.order_by(RFQ.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        return list(result.scalars().all()), total

    async def list_received(
        self, company_id: str, page: int = 1, page_size: int = 20,
    ) -> tuple[list[RFQ], int]:
        """List RFQs where company has been invited."""
        invited_rfq_ids = (
            select(RFQInvitation.rfq_id)
            .where(RFQInvitation.company_id == company_id)
        )
        query = (
            select(RFQ)
            .options(
                selectinload(RFQ.buyer_company),
                selectinload(RFQ.invitations),
            )
            .where(
                RFQ.id.in_(invited_rfq_ids),
                RFQ.status != RFQStatus.DRAFT,
            )
        )
        count_query = (
            select(func.count()).select_from(RFQ)
            .where(
                RFQ.id.in_(invited_rfq_ids),
                RFQ.status != RFQStatus.DRAFT,
            )
        )

        total = (await self.db.execute(count_query)).scalar_one()
        query = query.order_by(RFQ.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        return list(result.scalars().all()), total

    async def add_attachment(self, attachment: RFQAttachment) -> RFQAttachment:
        self.db.add(attachment)
        await self.db.flush()
        return attachment

    async def add_invitation(self, invitation: RFQInvitation) -> RFQInvitation:
        self.db.add(invitation)
        await self.db.flush()
        return invitation

    async def get_invitation(self, rfq_id: str, company_id: str) -> RFQInvitation | None:
        result = await self.db.execute(
            select(RFQInvitation).where(
                RFQInvitation.rfq_id == rfq_id,
                RFQInvitation.company_id == company_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_response(self, rfq_id: str, company_id: str) -> RFQResponse | None:
        result = await self.db.execute(
            select(RFQResponse)
            .options(selectinload(RFQResponse.company))
            .where(
                RFQResponse.rfq_id == rfq_id,
                RFQResponse.company_id == company_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_response_by_id(self, response_id: str) -> RFQResponse | None:
        result = await self.db.execute(
            select(RFQResponse)
            .options(selectinload(RFQResponse.company))
            .where(RFQResponse.id == response_id)
        )
        return result.scalar_one_or_none()

    async def create_response(self, response: RFQResponse) -> RFQResponse:
        self.db.add(response)
        await self.db.flush()
        return response

    async def list_responses(self, rfq_id: str) -> list[RFQResponse]:
        result = await self.db.execute(
            select(RFQResponse)
            .options(selectinload(RFQResponse.company))
            .where(RFQResponse.rfq_id == rfq_id)
            .order_by(RFQResponse.submitted_at)
        )
        return list(result.scalars().all())

    async def count_responses(self, rfq_id: str) -> int:
        result = await self.db.execute(
            select(func.count()).select_from(RFQResponse)
            .where(RFQResponse.rfq_id == rfq_id)
        )
        return result.scalar_one()

    async def add_status_history(self, entry: RFQStatusHistory) -> None:
        self.db.add(entry)
        await self.db.flush()
