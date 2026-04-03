from app.admin.repository import AdminRepository
from app.exceptions import BadRequestError, NotFoundError
from app.models.admin import AdminActionType, Shortlist
from app.models.user import User, UserStatus


class AdminService:
    def __init__(self, repo: AdminRepository):
        self.repo = repo

    async def get_dashboard_stats(self) -> dict:
        return await self.repo.get_dashboard_stats()

    # --- User management ---

    async def list_users(
        self, page: int = 1, page_size: int = 20,
        status_filter: str | None = None, search: str | None = None,
    ):
        return await self.repo.list_users(page, page_size, status_filter, search)

    async def suspend_user(self, user_id: str, admin: User) -> User:
        user = await self.repo.update_user_status(user_id, UserStatus.SUSPENDED)
        if not user:
            raise NotFoundError("User not found")
        await self.repo.log_action(
            admin.id, AdminActionType.USER_SUSPEND, "user", user_id,
        )
        return user

    async def activate_user(self, user_id: str, admin: User) -> User:
        user = await self.repo.update_user_status(user_id, UserStatus.ACTIVE)
        if not user:
            raise NotFoundError("User not found")
        await self.repo.log_action(
            admin.id, AdminActionType.USER_ACTIVATE, "user", user_id,
        )
        return user

    # --- Company management ---

    async def list_companies(
        self, page: int = 1, page_size: int = 20,
        verification_status: str | None = None, search: str | None = None,
    ):
        return await self.repo.list_companies(page, page_size, verification_status, search)

    # --- Action logs ---

    async def list_action_logs(
        self, page: int = 1, page_size: int = 20, admin_id: str | None = None,
    ):
        return await self.repo.list_action_logs(page, page_size, admin_id)

    # --- Shortlists (user-facing, not admin-only) ---

    async def add_to_shortlist(
        self, user: User, company_id: str | None = None,
        profile_id: str | None = None, note: str | None = None,
    ) -> Shortlist:
        if not company_id and not profile_id:
            raise BadRequestError("Must provide either company_id or profile_id")
        item = Shortlist(
            user_id=user.id,
            company_id=company_id,
            profile_id=profile_id,
            note=note,
        )
        return await self.repo.add_to_shortlist(item)

    async def remove_from_shortlist(self, shortlist_id: str, user: User) -> None:
        removed = await self.repo.remove_from_shortlist(shortlist_id, user.id)
        if not removed:
            raise NotFoundError("Shortlist item not found")

    async def list_shortlist(self, user: User, page: int = 1, page_size: int = 20):
        return await self.repo.list_shortlist(user.id, page, page_size)
