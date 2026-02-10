#!/usr/bin/env python
"""Setup script for Railway deployment - run migrations and create initial data."""
import asyncio
import sys
import os

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.models import User, Area
from app.core.security import get_password_hash
from app.models.user import Role
import uuid


async def migrate_and_setup():
    DATABASE_URL = os.environ.get("DATABASE_URL")

    if not DATABASE_URL:
        print("❌ DATABASE_URL environment variable not set")
        sys.exit(1)

    print(f"🔌 Connecting to database...")

    # Create engine
    engine = create_async_engine(DATABASE_URL, echo=False)

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("✅ Database tables created successfully!")

    # Create session
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Check if admin already exists
        from sqlalchemy import select
        result = await session.execute(select(User).where(User.staff_id == "ADMIN001"))
        existing_admin = result.scalar_one_or_none()

        if existing_admin:
            print("ℹ️  Super admin already exists, skipping creation...")
        else:
            # Create Super Admin
            admin = User(
                id=uuid.uuid4(),
                telegram_id=None,
                username=None,
                full_name="Super Admin",
                staff_id="ADMIN001",
                department="Administration",
                section="IT",
                role=Role.SUPER_ADMIN,
                password_hash=get_password_hash("admin123"),
                is_active=True,
            )
            session.add(admin)
            print("✅ Super admin created!")
            print("   Staff ID: ADMIN001")
            print("   Password: admin123")

        # Check if areas exist
        result = await session.execute(select(Area).limit(1))
        existing_area = result.scalar_one_or_none()

        if existing_area:
            print("ℹ️  Areas already exist, skipping creation...")
        else:
            # Create Areas
            areas = [
                Area(id=uuid.uuid4(), name="Production", description="Production department", parent_id=None, level=1),
                Area(id=uuid.uuid4(), name="Warehouse", description="Warehouse and storage", parent_id=None, level=1),
                Area(id=uuid.uuid4(), name="Office", description="Office and administration", parent_id=None, level=1),
            ]
            for area in areas:
                session.add(area)
            print("✅ Default areas created!")

        await session.commit()

    await engine.dispose()
    print("\n🎉 Setup complete!")


if __name__ == "__main__":
    asyncio.run(migrate_and_setup())
