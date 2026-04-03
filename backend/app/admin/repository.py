from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin import AdminActionLog, AdminActionType, Shortlist
from app.models.company import Company, VerificationStatusEnum
from app.models.review import Review, ReviewFlag
from app.models.user import User, UserStatus
from app.models.verification import VerificationRequest


class AdminRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # --- Dashboard stats ---

    async def get_dashboard_stats(self) -> dict:
        total_users = (
            await self.db.execute(select(func.count()).select_from(User))
        ).scalar_one()
        total_companies = (
            await self.db.execute(select(func.count()).select_from(Company))
        ).scalar_one()
        pending_verifications = (
            await self.db.execute(
                select(func.count())
                .select_from(VerificationRequest)
                .where(VerificationRequest.status == "pending")
            )
        ).scalar_one()
        flagged_reviews = (
            await self.db.execute(
                select(func.count(func.distinct(ReviewFlag.review_id)))
                .select_from(ReviewFlag)
                .where(ReviewFlag.resolved == False)
            )
        ).scalar_one()
        verified_companies = (
            await self.db.execute(
                select(func.count())
                .select_from(Company)
                .where(Company.verification_status == VerificationStatusEnum.APPROVED)
            )
        ).scalar_one()

        return {
            "total_users": total_users,
            "total_companies": total_companies,
            "verified_companies": verified_companies,
            "pending_verifications": pending_verifications,
            "flagged_reviews": flagged_reviews,
        }

    # --- User management ---

    async def list_users(
        self,
        page: int = 1,
        page_size: int = 20,
        status_filter: str | None = None,
        search: str | None = None,
    ) -> tuple[list[User], int]:
        query = select(User).order_by(User.created_at.desc())
        count_query = select(func.count()).select_from(User)

        if status_filter:
            query = query.where(User.status == status_filter)
            count_query = count_query.where(User.status == status_filter)

        if search:
            search_filter = (
                User.email.ilike(f"%{search}%")
                | User.first_name.ilike(f"%{search}%")
                | User.last_name.ilike(f"%{search}%")
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        total = (await self.db.execute(count_query)).scalar_one()
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        return list(result.scalars().all()), total

    async def get_user_by_id(self, user_id: str) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def update_user_status(self, user_id: str, status: UserStatus) -> User | None:
        user = await self.get_user_by_id(user_id)
        if user:
            user.status = status
            await self.db.flush()
        return user

    # --- Company management ---

    async def list_companies(
        self,
        page: int = 1,
        page_size: int = 20,
        verification_status: str | None = None,
        search: str | None = None,
    ) -> tuple[list[Company], int]:
        query = select(Company).order_by(Company.created_at.desc())
        count_query = select(func.count()).select_from(Company)

        if verification_status:
            query = query.where(Company.verification_status == verification_status)
            count_query = count_query.where(
                Company.verification_status == verification_status
            )

        if search:
            search_filter = (
                Company.name.ilike(f"%{search}%")
                | Company.email.ilike(f"%{search}%")
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        total = (await self.db.execute(count_query)).scalar_one()
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        return list(result.scalars().all()), total

    # --- Action logs ---

    async def log_action(
        self,
        admin_id: str,
        action_type: AdminActionType,
        target_type: str,
        target_id: str,
        details: dict | None = None,
    ) -> AdminActionLog:
        log = AdminActionLog(
            admin_id=admin_id,
            action_type=action_type,
            target_type=target_type,
            target_id=target_id,
            details=details,
        )
        self.db.add(log)
        await self.db.flush()
        return log

    async def list_action_logs(
        self,
        page: int = 1,
        page_size: int = 20,
        admin_id: str | None = None,
    ) -> tuple[list[AdminActionLog], int]:
        query = (
            select(AdminActionLog).order_by(AdminActionLog.created_at.desc())
        )
        count_query = select(func.count()).select_from(AdminActionLog)

        if admin_id:
            query = query.where(AdminActionLog.admin_id == admin_id)
            count_query = count_query.where(AdminActionLog.admin_id == admin_id)

        total = (await self.db.execute(count_query)).scalar_one()
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        return list(result.scalars().all()), total

    # --- Shortlists ---

    async def add_to_shortlist(self, shortlist: Shortlist) -> Shortlist:
        self.db.add(shortlist)
        await self.db.flush()
        return shortlist

    async def remove_from_shortlist(self, shortlist_id: str, user_id: str) -> bool:
        item = (
            await self.db.execute(
                select(Shortlist).where(
                    Shortlist.id == shortlist_id, Shortlist.user_id == user_id
                )
            )
        ).scalar_one_or_none()
        if item:
            await self.db.delete(item)
            await self.db.flush()
            return True
        return False

    async def list_shortlist(
        self, user_id: str, page: int = 1, page_size: int = 20
    ) -> tuple[list[Shortlist], int]:
        query = (
            select(Shortlist)
            .where(Shortlist.user_id == user_id)
            .order_by(Shortlist.created_at.desc())
        )
        count_query = (
            select(func.count())
            .select_from(Shortlist)
            .where(Shortlist.user_id == user_id)
        )

        total = (await self.db.execute(count_query)).scalar_one()
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        return list(result.scalars().all()), total
