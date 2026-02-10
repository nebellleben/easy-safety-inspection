"""User repository."""
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import Role, User


class UserRepository:
    """Repository for User model operations."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize repository."""
        self.db = db

    async def get_by_id(self, user_id: str | uuid.UUID) -> User | None:
        """Get user by ID."""
        result = await self.db.execute(
            select(User).where(User.id == uuid.UUID(user_id))
        )
        return result.scalar_one_or_none()

    async def get_by_staff_id(self, staff_id: str) -> User | None:
        """Get user by staff ID."""
        result = await self.db.execute(
            select(User).where(User.staff_id == staff_id)
        )
        return result.scalar_one_or_none()

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        """Get user by Telegram ID."""
        result = await self.db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def list_users(
        self,
        role: Role | None = None,
        is_active: bool | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> tuple[list[User], int]:
        """List users with optional filtering."""
        query = select(User)

        if role:
            query = query.where(User.role == role)
        if is_active is not None:
            query = query.where(User.is_active == is_active)

        # Get total count
        count_query = select(User.id)
        if role:
            count_query = count_query.where(User.role == role)
        if is_active is not None:
            count_query = count_query.where(User.is_active == is_active)

        count_result = await self.db.execute(count_query)
        total = len(count_result.all())

        # Get paginated results
        query = query.offset(offset).limit(limit).order_by(User.created_at.desc())
        result = await self.db.execute(query)
        users = list(result.scalars().all())

        return users, total

    async def create(self, user_data: dict[str, Any]) -> User:
        """Create a new user."""
        user = User(**user_data)
        self.db.add(user)
        await self.db.flush()
        return user

    async def update(self, user: User, update_data: dict[str, Any]) -> User:
        """Update a user."""
        for field, value in update_data.items():
            if hasattr(user, field) and value is not None:
                setattr(user, field, value)
        await self.db.flush()
        return user

    async def delete(self, user: User) -> None:
        """Delete (soft delete) a user."""
        user.is_active = False
        await self.db.flush()

    async def get_admins_for_area(self, area_id: uuid.UUID) -> list[User]:
        """Get all admins assigned to a specific area."""
        # This will need to join with user_areas table when implemented
        # For now, return all admins
        result = await self.db.execute(
            select(User).where(User.role.in_([Role.ADMIN, Role.SUPER_ADMIN]))
        )
        return list(result.scalars().all())
