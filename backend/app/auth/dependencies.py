from typing import Annotated

from fastapi import Depends, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.exceptions import ForbiddenError, UnauthorizedError
from app.auth.utils import decode_access_token
from app.models.user import AccountType, User, UserStatus


async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    authorization: Annotated[str | None, Header()] = None,
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise UnauthorizedError("Missing or invalid authorization header")

    token = authorization.removeprefix("Bearer ")

    try:
        payload = decode_access_token(token)
    except Exception:
        raise UnauthorizedError("Invalid or expired token")

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedError("Invalid token payload")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise UnauthorizedError("User not found")
    if user.status != UserStatus.ACTIVE:
        raise ForbiddenError("Account is suspended or deactivated")

    return user


# Dependency factories for role-based access
def require_account_types(*allowed_types: AccountType):
    async def _check(user: Annotated[User, Depends(get_current_user)]) -> User:
        if user.account_type not in allowed_types:
            raise ForbiddenError("Your account type does not have access to this resource")
        return user
    return _check


def require_admin():
    return require_account_types(AccountType.ADMIN)


def require_verified_email(user: Annotated[User, Depends(get_current_user)]) -> User:
    if not user.email_verified:
        raise ForbiddenError("Email verification required")
    return user


# Commonly used dependency annotations
CurrentUser = Annotated[User, Depends(get_current_user)]
AdminUser = Annotated[User, Depends(require_account_types(AccountType.ADMIN))]
VerifiedUser = Annotated[User, Depends(require_verified_email)]
BuyerUser = Annotated[User, Depends(require_account_types(AccountType.BUYER))]
SupplierUser = Annotated[User, Depends(require_account_types(
    AccountType.SUPPLIER, AccountType.DISTRIBUTOR, AccountType.MANUFACTURER,
    AccountType.CONTRACTOR, AccountType.SUBCONTRACTOR,
))]
