"""Create initial areas."""
import asyncio
import sys

sys.path.insert(0, ".")

from app.db.session import async_session
from app.repositories.area import AreaRepository


async def create_initial_areas() -> None:
    """Create initial area structure."""
    async with async_session() as db:
        area_repo = AreaRepository(db)

        # Create top-level areas
        production = await area_repo.create({
            "name": "Production",
            "description": "Production department",
            "parent_id": None,
            "level": 1,
        })

        warehouse = await area_repo.create({
            "name": "Warehouse",
            "description": "Warehouse and storage",
            "parent_id": None,
            "level": 1,
        })

        office = await area_repo.create({
            "name": "Office",
            "description": "Office and administration",
            "parent_id": None,
            "level": 1,
        })

        await db.commit()

        print("✅ Initial areas created successfully!")
        print(f"   - {production.name}")
        print(f"   - {warehouse.name}")
        print(f"   - {office.name}")


if __name__ == "__main__":
    asyncio.run(create_initial_areas())
