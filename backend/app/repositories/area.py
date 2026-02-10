"""Area repository."""
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.area import Area


class AreaRepository:
    """Repository for Area model operations."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize repository."""
        self.db = db

    async def get_by_id(self, area_id: str | uuid.UUID) -> Area | None:
        """Get area by ID."""
        result = await self.db.execute(
            select(Area)
            .options(selectinload(Area.children))
            .where(Area.id == uuid.UUID(area_id))
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Area | None:
        """Get area by name."""
        result = await self.db.execute(
            select(Area).where(Area.name == name)
        )
        return result.scalar_one_or_none()

    async def list_areas(
        self,
        level: int | None = None,
        parent_id: uuid.UUID | None = None,
        include_children: bool = True,
    ) -> list[Area]:
        """List areas with optional filtering."""
        query = select(Area)

        if level:
            query = query.where(Area.level == level)
        if parent_id is not None:
            query = query.where(Area.parent_id == parent_id)

        if include_children:
            query = query.options(selectinload(Area.children))

        query = query.order_by(Area.name)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_tree(self) -> list[Area]:
        """Get all areas as a tree structure."""
        # Get all areas
        result = await self.db.execute(
            select(Area)
            .options(selectinload(Area.children))
            .where(Area.level == 1)
            .order_by(Area.name)
        )
        return list(result.scalars().all())

    async def create(self, area_data: dict[str, Any]) -> Area:
        """Create a new area."""
        area = Area(**area_data)
        self.db.add(area)
        await self.db.flush()
        return area

    async def update(self, area: Area, update_data: dict[str, Any]) -> Area:
        """Update an area."""
        for field, value in update_data.items():
            if hasattr(area, field) and value is not None:
                setattr(area, field, value)
        await self.db.flush()
        return area

    async def delete(self, area: Area) -> None:
        """Delete an area."""
        await self.db.delete(area)
        await self.db.flush()

    async def get_descendant_ids(self, area_id: uuid.UUID) -> list[uuid.UUID]:
        """Get all descendant area IDs for a given area."""
        # This should use a recursive CTE for proper implementation
        # For now, just return the area itself
        return [area_id]
