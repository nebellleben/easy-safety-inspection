#!/usr/bin/env python
"""Update areas in the database."""
import asyncio
import sys
import os

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, delete
from app.models import Area
import uuid


async def update_areas():
    DATABASE_URL = os.environ.get("DATABASE_URL")

    if not DATABASE_URL:
        print("DATABASE_URL environment variable not set")
        sys.exit(1)

    print(f"Connecting to database...")

    # Create engine
    engine = create_async_engine(DATABASE_URL, echo=False)

    # Create session
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Delete all existing areas
        await session.execute(delete(Area))
        print("Deleted existing areas")

        # Create new areas
        new_areas = [
            {"name": "Workshop", "description": "Workshop area"},
            {"name": "Equipment Room", "description": "Equipment storage room"},
            {"name": "Storage Room", "description": "Storage room"},
            {"name": "Trackside", "description": "Trackside area"},
            {"name": "Office", "description": "Office area"},
            {"name": "Others", "description": "Other areas"},
        ]

        for area_data in new_areas:
            area = Area(
                id=uuid.uuid4(),
                name=area_data["name"],
                description=area_data["description"],
                parent_id=None,
                level=1
            )
            session.add(area)
            print(f"Created area: {area_data['name']}")

        await session.commit()
        print("\nAreas updated successfully!")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(update_areas())
