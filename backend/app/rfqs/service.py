from datetime import datetime, timezone

from dateutil.parser import isoparse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import BadRequestError, ForbiddenError, NotFoundError
from app.models.company import CompanyMember, MemberRole
from app.models.notification import NotificationType
from app.models.rfq import (
    RFQ,
    RFQAttachment,
    RFQInvitation,
    RFQResponse,
    RFQResponseStatus,
    RFQStatus,
    RFQStatusHistory,
)
from app.models.user import AccountType, User
from app.rfqs.repository import RFQRepository
from app.workers.notifications import create_notification


class RFQService:
    def __init__(self, repo: RFQRepository, db: AsyncSession):
        self.repo = repo
        self.db = db

    async def create_rfq(self, user: User, company_id: str, **kwargs) -> RFQ:
        await self._require_buyer_role(company_id, user)

        deadline_str = kwargs.pop("deadline")
        deadline = isoparse(deadline_str)

        rfq = RFQ(
            company_id=company_id,
            created_by=user.id,
            deadline=deadline,
            **kwargs,
        )
        rfq = await self.repo.create(rfq)

        await self.repo.add_status_history(RFQStatusHistory(
            rfq_id=rfq.id,
            new_status=RFQStatus.DRAFT,
            changed_by=user.id,
        ))

        return await self.repo.get_by_id(rfq.id)

    async def get_rfq(self, rfq_id: str, user: User) -> RFQ:
        rfq = await self.repo.get_by_id(rfq_id)
        if not rfq:
            raise NotFoundError("RFQ not found")

        # Buyer company can always see their own RFQs
        if await self._is_company_member(rfq.company_id, user.id):
            return rfq

        # Invited company can see open RFQs
        if rfq.status != RFQStatus.DRAFT:
            inv = await self.repo.get_invitation(rfq_id, await self._get_user_company_id(user))
            if inv:
                # Mark as viewed
                if not inv.viewed_at:
                    inv.viewed_at = datetime.now(timezone.utc)
                    if inv.status == RFQResponseStatus.INVITED:
                        inv.status = RFQResponseStatus.VIEWED
                    await self.db.flush()
                return rfq

        if user.is_admin:
            return rfq

        raise ForbiddenError("You do not have access to this RFQ")

    async def list_rfqs(
        self, user: User, role: str, company_id: str,
        page: int = 1, page_size: int = 20, status: str | None = None,
    ) -> tuple[list[RFQ], list[int], int]:
        """Returns (rfqs, response_counts, total)."""
        if role == "buyer":
            rfqs, total = await self.repo.list_by_buyer(
                company_id, page=page, page_size=page_size, status=status,
            )
        else:
            rfqs, total = await self.repo.list_received(
                company_id, page=page, page_size=page_size,
            )

        counts = []
        for rfq in rfqs:
            c = await self.repo.count_responses(rfq.id)
            counts.append(c)

        return rfqs, counts, total

    async def update_rfq(self, rfq_id: str, user: User, **kwargs) -> RFQ:
        rfq = await self.repo.get_by_id(rfq_id)
        if not rfq:
            raise NotFoundError("RFQ not found")
        await self._require_buyer_role(rfq.company_id, user)

        if rfq.status != RFQStatus.DRAFT:
            raise BadRequestError("Only draft RFQs can be edited")

        if "deadline" in kwargs and kwargs["deadline"]:
            kwargs["deadline"] = isoparse(kwargs["deadline"])

        for key, value in kwargs.items():
            if value is not None and hasattr(rfq, key):
                setattr(rfq, key, value)

        await self.db.flush()
        return await self.repo.get_by_id(rfq_id)

    async def publish_rfq(self, rfq_id: str, user: User) -> RFQ:
        rfq = await self.repo.get_by_id(rfq_id)
        if not rfq:
            raise NotFoundError("RFQ not found")
        await self._require_buyer_role(rfq.company_id, user)

        if rfq.status != RFQStatus.DRAFT:
            raise BadRequestError("Only draft RFQs can be published")

        await self._change_status(rfq, RFQStatus.OPEN, user)

        # Notify invited companies
        for inv in rfq.invitations:
            members = await self.db.execute(
                select(CompanyMember).where(CompanyMember.company_id == inv.company_id)
            )
            for member in members.scalars():
                await create_notification(
                    self.db, member.user_id,
                    NotificationType.RFQ_RECEIVED,
                    f"New RFQ: {rfq.title}",
                    f"You have been invited to respond to an RFQ.",
                    link=f"/rfqs/{rfq.id}",
                )

        await self.db.flush()
        return await self.repo.get_by_id(rfq_id)

    async def close_rfq(self, rfq_id: str, user: User) -> RFQ:
        rfq = await self.repo.get_by_id(rfq_id)
        if not rfq:
            raise NotFoundError("RFQ not found")
        await self._require_buyer_role(rfq.company_id, user)
        if rfq.status != RFQStatus.OPEN:
            raise BadRequestError("Only open RFQs can be closed")
        await self._change_status(rfq, RFQStatus.CLOSED, user)
        await self.db.flush()
        return await self.repo.get_by_id(rfq_id)

    async def cancel_rfq(self, rfq_id: str, user: User) -> RFQ:
        rfq = await self.repo.get_by_id(rfq_id)
        if not rfq:
            raise NotFoundError("RFQ not found")
        await self._require_buyer_role(rfq.company_id, user)
        if rfq.status in (RFQStatus.AWARDED, RFQStatus.CANCELLED):
            raise BadRequestError("Cannot cancel this RFQ")
        await self._change_status(rfq, RFQStatus.CANCELLED, user)
        await self.db.flush()
        return await self.repo.get_by_id(rfq_id)

    async def award_rfq(self, rfq_id: str, user: User, awarded_company_id: str) -> RFQ:
        rfq = await self.repo.get_by_id(rfq_id)
        if not rfq:
            raise NotFoundError("RFQ not found")
        await self._require_buyer_role(rfq.company_id, user)
        if rfq.status not in (RFQStatus.OPEN, RFQStatus.CLOSED):
            raise BadRequestError("RFQ must be open or closed to award")

        rfq.awarded_to = awarded_company_id
        await self._change_status(rfq, RFQStatus.AWARDED, user)
        await self.db.flush()
        return await self.repo.get_by_id(rfq_id)

    async def invite_companies(
        self, rfq_id: str, user: User, company_ids: list[str]
    ) -> list[RFQInvitation]:
        rfq = await self.repo.get_by_id(rfq_id)
        if not rfq:
            raise NotFoundError("RFQ not found")
        await self._require_buyer_role(rfq.company_id, user)

        invitations = []
        for cid in company_ids:
            existing = await self.repo.get_invitation(rfq_id, cid)
            if existing:
                continue
            inv = RFQInvitation(rfq_id=rfq_id, company_id=cid)
            inv = await self.repo.add_invitation(inv)
            invitations.append(inv)

            # If RFQ is already open, notify immediately
            if rfq.status == RFQStatus.OPEN:
                members = await self.db.execute(
                    select(CompanyMember).where(CompanyMember.company_id == cid)
                )
                for member in members.scalars():
                    await create_notification(
                        self.db, member.user_id,
                        NotificationType.RFQ_RECEIVED,
                        f"New RFQ: {rfq.title}",
                        "You have been invited to respond to an RFQ.",
                        link=f"/rfqs/{rfq.id}",
                    )

        await self.db.flush()
        return invitations

    async def submit_response(
        self, rfq_id: str, user: User, **kwargs
    ) -> RFQResponse:
        rfq = await self.repo.get_by_id(rfq_id)
        if not rfq:
            raise NotFoundError("RFQ not found")
        if rfq.status != RFQStatus.OPEN:
            raise BadRequestError("RFQ is not accepting responses")
        if rfq.deadline < datetime.now(timezone.utc):
            raise BadRequestError("RFQ deadline has passed")

        company_id = await self._get_user_company_id(user)
        inv = await self.repo.get_invitation(rfq_id, company_id)
        if not inv:
            raise ForbiddenError("Your company was not invited to this RFQ")

        existing = await self.repo.get_response(rfq_id, company_id)
        if existing:
            raise BadRequestError("Your company has already submitted a response")

        response = RFQResponse(
            rfq_id=rfq_id,
            company_id=company_id,
            submitted_by=user.id,
            **kwargs,
        )
        response = await self.repo.create_response(response)

        # Update invitation status
        inv.status = RFQResponseStatus.SUBMITTED

        # Notify buyer
        await create_notification(
            self.db, rfq.created_by,
            NotificationType.RFQ_RESPONSE_SUBMITTED,
            f"New response to: {rfq.title}",
            "A vendor has submitted a response to your RFQ.",
            link=f"/rfqs/{rfq.id}/responses",
        )

        await self.db.flush()
        return response

    async def update_response(
        self, rfq_id: str, response_id: str, user: User, **kwargs
    ) -> RFQResponse:
        rfq = await self.repo.get_by_id(rfq_id)
        if not rfq:
            raise NotFoundError("RFQ not found")
        if rfq.status != RFQStatus.OPEN:
            raise BadRequestError("RFQ is not open")
        if rfq.deadline < datetime.now(timezone.utc):
            raise BadRequestError("RFQ deadline has passed")

        resp = await self.repo.get_response_by_id(response_id)
        if not resp or resp.rfq_id != rfq_id:
            raise NotFoundError("Response not found")

        company_id = await self._get_user_company_id(user)
        if resp.company_id != company_id:
            raise ForbiddenError("You can only edit your own company's response")

        for key, value in kwargs.items():
            if value is not None and hasattr(resp, key):
                setattr(resp, key, value)

        resp.status = RFQResponseStatus.REVISED
        await self.db.flush()
        return resp

    async def list_responses(self, rfq_id: str, user: User) -> list[RFQResponse]:
        rfq = await self.repo.get_by_id(rfq_id)
        if not rfq:
            raise NotFoundError("RFQ not found")

        # Only buyer company can see all responses
        if not await self._is_company_member(rfq.company_id, user.id) and not user.is_admin:
            raise ForbiddenError("Only the buyer can view all responses")

        return await self.repo.list_responses(rfq_id)

    async def add_attachment(
        self, rfq_id: str, user: User, file_url: str, file_name: str, file_size: int | None
    ) -> RFQAttachment:
        rfq = await self.repo.get_by_id(rfq_id)
        if not rfq:
            raise NotFoundError("RFQ not found")
        await self._require_buyer_role(rfq.company_id, user)

        att = RFQAttachment(
            rfq_id=rfq_id,
            file_url=file_url,
            file_name=file_name,
            file_size=file_size,
        )
        return await self.repo.add_attachment(att)

    # --- Helpers ---

    async def _change_status(self, rfq: RFQ, new_status: RFQStatus, user: User) -> None:
        old_status = rfq.status
        rfq.status = new_status
        await self.repo.add_status_history(RFQStatusHistory(
            rfq_id=rfq.id,
            old_status=old_status,
            new_status=new_status,
            changed_by=user.id,
        ))

    async def _require_buyer_role(self, company_id: str, user: User) -> None:
        if user.is_admin:
            return
        if not await self._is_company_member(company_id, user.id):
            raise ForbiddenError("You are not a member of the buyer company")

    async def _is_company_member(self, company_id: str, user_id: str) -> bool:
        result = await self.db.execute(
            select(CompanyMember).where(
                CompanyMember.company_id == company_id,
                CompanyMember.user_id == user_id,
            )
        )
        return result.scalar_one_or_none() is not None

    async def _get_user_company_id(self, user: User) -> str:
        """Get the primary company ID for a user."""
        result = await self.db.execute(
            select(CompanyMember).where(
                CompanyMember.user_id == user.id,
                CompanyMember.is_primary.is_(True),
            )
        )
        member = result.scalar_one_or_none()
        if not member:
            # Fallback: get any company
            result = await self.db.execute(
                select(CompanyMember).where(CompanyMember.user_id == user.id).limit(1)
            )
            member = result.scalar_one_or_none()
        if not member:
            raise BadRequestError("You are not associated with any company")
        return member.company_id
