"""Setup endpoint for initial deployment configuration."""
import asyncio
import os
import uuid

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.db.base import Base
from app.models import User, Area
from app.core.security import get_password_hash
from app.models.user import Role
from app.core.deps import CurrentSuperAdmin

router = APIRouter()
engine = None
async_session = None


def get_engine():
    global engine, async_session
    if engine is None:
        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="DATABASE_URL not configured",
            )
        engine = create_async_engine(database_url, echo=False)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    return engine, async_session


@router.post("/run-migrations")
async def run_migrations(_: CurrentSuperAdmin):
    """Run database migrations and create initial data."""
    engine, async_session = get_engine()

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    return {"status": "success", "message": "Database migrations completed"}


@router.post("/setup-initial-data")
async def setup_initial_data(_: CurrentSuperAdmin):
    """Create initial super admin and default areas."""
    engine, async_session = get_engine()

    async with async_session() as session:
        # Check if admin already exists
        result = await session.execute(select(User).where(User.staff_id == "ADMIN001"))
        existing_admin = result.scalar_one_or_none()

        if existing_admin:
            return {"status": "already_exists", "message": "Super admin already exists"}

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

        # Create Areas
        areas = [
            Area(id=uuid.uuid4(), name="Production", description="Production department", parent_id=None, level=1),
            Area(id=uuid.uuid4(), name="Warehouse", description="Warehouse and storage", parent_id=None, level=1),
            Area(id=uuid.uuid4(), name="Office", description="Office and administration", parent_id=None, level=1),
        ]
        for area in areas:
            session.add(area)

        await session.commit()

        return {
            "status": "success",
            "message": "Initial data created",
            "admin": {"staff_id": "ADMIN001", "password": "admin123"}
        }


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "setup"}
