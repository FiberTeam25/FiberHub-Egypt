from app.exceptions import NotFoundError
from app.models.user import User
from app.users.repository import UserRepository


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def get_user_public(self, user_id: str) -> User:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        return user

    async def update_user(self, user: User, **kwargs) -> User:
        return await self.repo.update(user, **kwargs)
