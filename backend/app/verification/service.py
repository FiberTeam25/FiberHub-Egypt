from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import BadRequestError, ForbiddenError, NotFoundError
from app.models.admin import AdminActionLog, AdminActionType
from app.models.company import Company, CompanyMember, MemberRole, VerificationStatusEnum
from app.models.notification import NotificationType
from app.models.profile import IndividualProfile
from app.models.user import User
from app.models.verification import VerificationDocument, VerificationRequest
from app.verification.repository import VerificationRepository
from app.workers.notifications import create_notification


class VerificationService:
    def __init__(self, repo: VerificationRepository, db: AsyncSession):
        self.repo = repo
        self.db = db

    async def submit_verification(
        self,
        user: User,
        company_id: str | None,
        profile_id: str | None,
        documents: list[dict],
    ) -> VerificationRequest:
        if not company_id and not profile_id:
            raise BadRequestError("Either company_id or profile_id is required")

        # Verify ownership
        if company_id:
            await self._require_company_admin(company_id, user)
        if profile_id:
            profile = await self.db.execute(
                select(IndividualProfile).where(IndividualProfile.id == profile_id)
            )
            p = profile.scalar_one_or_none()
            if not p or (p.user_id != user.id and not user.is_admin):
                raise ForbiddenError("You can only submit verification for your own profile")

        if not documents:
            raise BadRequestError("At least one document is required")

        request = VerificationRequest(
            company_id=company_id,
            profile_id=profile_id,
            status=VerificationStatusEnum.PENDING,
        )
        request = await self.repo.create(request)

        for doc_data in documents:
            doc = VerificationDocument(
                verification_request_id=request.id,
                document_type=doc_data["document_type"],
                file_url=doc_data["file_url"],
                file_name=doc_data["file_name"],
            )
            await self.repo.add_document(doc)

        # Update entity verification status
        if company_id:
            company = await self.db.execute(
                select(Company).where(Company.id == company_id)
            )
            c = company.scalar_one()
            c.verification_status = VerificationStatusEnum.PENDING

        if profile_id:
            profile_result = await self.db.execute(
                select(IndividualProfile).where(IndividualProfile.id == profile_id)
            )
            prof = profile_result.scalar_one()
            prof.verification_status = VerificationStatusEnum.PENDING

        await self.db.flush()

        # Reload with documents
        return await self.repo.get_by_id(request.id)

    async def get_status(self, user: User, company_id: str | None, profile_id: str | None):
        if company_id:
            return await self.repo.get_latest_for_company(company_id)
        if profile_id:
            return await self.repo.get_latest_for_profile(profile_id)
        # Try to find for user's own entities
        # Check individual profile
        result = await self.db.execute(
            select(IndividualProfile).where(IndividualProfile.user_id == user.id)
        )
        profile = result.scalar_one_or_none()
        if profile:
            return await self.repo.get_latest_for_profile(profile.id)
        return None

    async def get_queue(
        self, page: int = 1, page_size: int = 20, status: str | None = None
    ) -> tuple[list[VerificationRequest], int]:
        return await self.repo.list_pending(page=page, page_size=page_size, status=status)

    async def get_request_detail(self, request_id: str) -> VerificationRequest:
        req = await self.repo.get_by_id(request_id)
        if not req:
            raise NotFoundError("Verification request not found")
        return req

    async def approve(
        self, request_id: str, admin: User, admin_notes: str | None = None
    ) -> VerificationRequest:
        req = await self.get_request_detail(request_id)
        if req.status != VerificationStatusEnum.PENDING:
            raise BadRequestError("Only pending requests can be approved")

        req.status = VerificationStatusEnum.APPROVED
        req.reviewed_at = datetime.now(timezone.utc)
        req.reviewed_by = admin.id
        req.admin_notes = admin_notes

        # Update entity
        target_user_id = await self._update_entity_status(
            req, VerificationStatusEnum.APPROVED
        )

        # Log admin action
        self.db.add(AdminActionLog(
            admin_id=admin.id,
            action_type=AdminActionType.VERIFY_APPROVE,
            target_type="company" if req.company_id else "profile",
            target_id=req.company_id or req.profile_id,
            details={"request_id": req.id, "notes": admin_notes},
        ))

        # Notify user
        if target_user_id:
            await create_notification(
                self.db, target_user_id,
                NotificationType.VERIFICATION_APPROVED,
                "Verification Approved",
                "Your verification has been approved. Your profile now shows the verified badge.",
                link="/company/verification" if req.company_id else "/profile",
            )

        await self.db.flush()
        return req

    async def reject(
        self, request_id: str, admin: User, admin_notes: str | None = None
    ) -> VerificationRequest:
        req = await self.get_request_detail(request_id)
        if req.status != VerificationStatusEnum.PENDING:
            raise BadRequestError("Only pending requests can be rejected")

        req.status = VerificationStatusEnum.REJECTED
        req.reviewed_at = datetime.now(timezone.utc)
        req.reviewed_by = admin.id
        req.admin_notes = admin_notes

        target_user_id = await self._update_entity_status(
            req, VerificationStatusEnum.REJECTED
        )

        self.db.add(AdminActionLog(
            admin_id=admin.id,
            action_type=AdminActionType.VERIFY_REJECT,
            target_type="company" if req.company_id else "profile",
            target_id=req.company_id or req.profile_id,
            details={"request_id": req.id, "notes": admin_notes},
        ))

        if target_user_id:
            await create_notification(
                self.db, target_user_id,
                NotificationType.VERIFICATION_REJECTED,
                "Verification Rejected",
                f"Your verification was rejected. {admin_notes or 'Please review the requirements and resubmit.'}",
                link="/company/verification" if req.company_id else "/profile",
            )

        await self.db.flush()
        return req

    async def _update_entity_status(
        self, req: VerificationRequest, status: VerificationStatusEnum
    ) -> str | None:
        """Update the company or profile verification status. Returns user_id for notifications."""
        if req.company_id:
            result = await self.db.execute(
                select(Company).where(Company.id == req.company_id)
            )
            company = result.scalar_one()
            company.verification_status = status
            # Find primary member for notification
            member_result = await self.db.execute(
                select(CompanyMember).where(
                    CompanyMember.company_id == req.company_id,
                    CompanyMember.is_primary.is_(True),
                )
            )
            member = member_result.scalar_one_or_none()
            return member.user_id if member else None

        if req.profile_id:
            result = await self.db.execute(
                select(IndividualProfile).where(IndividualProfile.id == req.profile_id)
            )
            profile = result.scalar_one()
            profile.verification_status = status
            return profile.user_id

        return None

    async def _require_company_admin(self, company_id: str, user: User) -> None:
        if user.is_admin:
            return
        result = await self.db.execute(
            select(CompanyMember).where(
                CompanyMember.company_id == company_id,
                CompanyMember.user_id == user.id,
            )
        )
        member = result.scalar_one_or_none()
        if not member or member.role not in (MemberRole.OWNER, MemberRole.ADMIN):
            raise ForbiddenError("You must be a company owner or admin")
