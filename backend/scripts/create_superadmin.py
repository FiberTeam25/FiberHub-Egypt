"""
Create a superadmin user via CLI.

Usage:
    python -m scripts.create_superadmin --email admin@fiberhub.eg --password <password>
"""

import argparse
import asyncio
import sys

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

sys.path.insert(0, ".")

from app.config import get_settings
from app.database import async_session_factory, engine
from app.auth.utils import hash_password
from app.models.user import AccountType, User


async def create_admin(email: str, password: str, first_name: str, last_name: str) -> None:
    async with async_session_factory() as db:
        # Check if already exists
        result = await db.execute(select(User).where(User.email == email))
        existing = result.scalar_one_or_none()
        if existing:
            print(f"User with email {email} already exists.")
            return

        user = User(
            email=email,
            password_hash=hash_password(password),
            first_name=first_name,
            last_name=last_name,
            account_type=AccountType.ADMIN,
            email_verified=True,
        )
        db.add(user)
        await db.commit()
        print(f"Admin user created: {email} (ID: {user.id})")


def main():
    parser = argparse.ArgumentParser(description="Create a FiberHub superadmin user")
    parser.add_argument("--email", required=True, help="Admin email")
    parser.add_argument("--password", required=True, help="Admin password")
    parser.add_argument("--first-name", default="Admin", help="First name")
    parser.add_argument("--last-name", default="FiberHub", help="Last name")
    args = parser.parse_args()

    asyncio.run(create_admin(args.email, args.password, args.first_name, args.last_name))


if __name__ == "__main__":
    main()
