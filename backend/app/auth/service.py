import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import BadRequestError, ConflictError, UnauthorizedError
from app.models.user import (
    AccountType,
    EmailVerificationToken,
    PasswordResetToken,
    RefreshToken,
    User,
)
from app.auth.utils import (
    create_access_token,
    create_refresh_token,
    generate_verification_token,
    get_password_reset_token_expiry,
    get_refresh_token_expiry,
    get_verification_token_expiry,
    hash_password,
    hash_token,
    verify_password,
)

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(
        self,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        phone: str | None,
        account_type: AccountType,
    ) -> tuple[User, str]:
        """Register a new user. Returns (user, verification_token)."""
        # Prevent self-registration as admin
        if account_type == AccountType.ADMIN:
            raise BadRequestError("Admin accounts cannot be created through registration")

        # Check for existing user
        result = await self.db.execute(select(User).where(User.email == email))
        if result.scalar_one_or_none():
            raise ConflictError("A user with this email already exists")

        user = User(
            email=email,
            password_hash=hash_password(password),
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            account_type=account_type,
        )
        self.db.add(user)
        await self.db.flush()

        # Create email verification token
        token = generate_verification_token()
        verification = EmailVerificationToken(
            user_id=user.id,
            token=token,
            expires_at=get_verification_token_expiry(),
        )
        self.db.add(verification)
        await self.db.flush()

        logger.info("User registered: %s (%s)", email, account_type.value)
        return user, token

    async def login(self, email: str, password: str) -> tuple[str, str, User]:
        """Authenticate user. Returns (access_token, refresh_token, user)."""
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user or not verify_password(password, user.password_hash):
            raise UnauthorizedError("Invalid email or password")

        if not user.is_active:
            raise UnauthorizedError("Account is suspended or deactivated")

        # Create tokens
        access_token = create_access_token(user.id, user.account_type.value)
        raw_refresh = create_refresh_token()

        refresh_record = RefreshToken(
            user_id=user.id,
            token_hash=hash_token(raw_refresh),
            expires_at=get_refresh_token_expiry(),
        )
        self.db.add(refresh_record)

        # Update last login
        user.last_login_at = datetime.now(timezone.utc)
        await self.db.flush()

        logger.info("User logged in: %s", email)
        return access_token, raw_refresh, user

    async def refresh_access_token(self, raw_refresh_token: str) -> tuple[str, str]:
        """Validate refresh token and issue new token pair. Returns (access_token, new_refresh)."""
        token_hash = hash_token(raw_refresh_token)
        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.revoked_at.is_(None),
            )
        )
        refresh = result.scalar_one_or_none()

        if not refresh:
            raise UnauthorizedError("Invalid refresh token")

        if refresh.expires_at < datetime.now(timezone.utc):
            raise UnauthorizedError("Refresh token expired")

        # Get user
        result = await self.db.execute(select(User).where(User.id == refresh.user_id))
        user = result.scalar_one_or_none()
        if not user or not user.is_active:
            raise UnauthorizedError("User not found or inactive")

        # Revoke old refresh token (rotation)
        refresh.revoked_at = datetime.now(timezone.utc)

        # Issue new pair
        new_access = create_access_token(user.id, user.account_type.value)
        new_raw_refresh = create_refresh_token()
        new_refresh_record = RefreshToken(
            user_id=user.id,
            token_hash=hash_token(new_raw_refresh),
            expires_at=get_refresh_token_expiry(),
        )
        self.db.add(new_refresh_record)
        await self.db.flush()

        return new_access, new_raw_refresh

    async def logout(self, raw_refresh_token: str) -> None:
        """Revoke a refresh token."""
        token_hash = hash_token(raw_refresh_token)
        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        refresh = result.scalar_one_or_none()
        if refresh:
            refresh.revoked_at = datetime.now(timezone.utc)
            await self.db.flush()

    async def verify_email(self, token: str) -> User:
        """Verify user email with token."""
        result = await self.db.execute(
            select(EmailVerificationToken).where(
                EmailVerificationToken.token == token,
                EmailVerificationToken.used_at.is_(None),
            )
        )
        record = result.scalar_one_or_none()

        if not record:
            raise BadRequestError("Invalid verification token")

        if record.expires_at < datetime.now(timezone.utc):
            raise BadRequestError("Verification token has expired")

        # Mark token as used
        record.used_at = datetime.now(timezone.utc)

        # Mark user as verified
        result = await self.db.execute(select(User).where(User.id == record.user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise BadRequestError("User not found")

        user.email_verified = True
        await self.db.flush()

        logger.info("Email verified: %s", user.email)
        return user

    async def create_password_reset_token(self, email: str) -> str | None:
        """Create a password reset token. Returns token or None if user not found.
        Always returns success to the caller to prevent email enumeration.
        """
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user:
            return None

        token = generate_verification_token()
        reset = PasswordResetToken(
            user_id=user.id,
            token=token,
            expires_at=get_password_reset_token_expiry(),
        )
        self.db.add(reset)
        await self.db.flush()

        logger.info("Password reset requested: %s", email)
        return token

    async def reset_password(self, token: str, new_password: str) -> None:
        """Reset user password with valid token."""
        result = await self.db.execute(
            select(PasswordResetToken).where(
                PasswordResetToken.token == token,
                PasswordResetToken.used_at.is_(None),
            )
        )
        record = result.scalar_one_or_none()

        if not record:
            raise BadRequestError("Invalid reset token")

        if record.expires_at < datetime.now(timezone.utc):
            raise BadRequestError("Reset token has expired")

        # Mark token as used
        record.used_at = datetime.now(timezone.utc)

        # Update password
        result = await self.db.execute(select(User).where(User.id == record.user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise BadRequestError("User not found")

        user.password_hash = hash_password(new_password)
        await self.db.flush()

        logger.info("Password reset completed: %s", user.email)
