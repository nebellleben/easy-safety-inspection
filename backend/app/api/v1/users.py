"""User management API endpoints (admin only)."""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentSuperAdmin, DbSession
from app.core.security import get_password_hash
from app.models.user import Role
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter()


@router.get("", response_model=list[UserResponse])
async def list_users(
    db: DbSession,
    current_admin: CurrentSuperAdmin,
    role: Role | None = None,
    is_active: bool | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=100),
):
    """List all users (super-admin only)."""
    user_repo = UserRepository(db)
    offset = (page - 1) * page_size
    users, total = await user_repo.list_users(
        role=role,
        is_active=is_active,
        offset=offset,
        limit=page_size,
    )
    return [UserResponse.model_validate(u) for u in users]


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: uuid.UUID,
    db: DbSession,
    current_admin: CurrentSuperAdmin,
):
    """Get user details (super-admin only)."""
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserResponse.model_validate(user)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: DbSession,
    current_admin: CurrentSuperAdmin,
):
    """Create a new user (super-admin only)."""
    user_repo = UserRepository(db)

    # Check if staff ID already exists
    existing = await user_repo.get_by_staff_id(user_data.staff_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this staff ID already exists",
        )

    # Hash password if provided
    create_data = user_data.model_dump(exclude={"password"})
    if user_data.password:
        create_data["password_hash"] = get_password_hash(user_data.password)

    user = await user_repo.create(create_data)
    return UserResponse.model_validate(user)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: uuid.UUID,
    user_data: UserUpdate,
    db: DbSession,
    current_admin: CurrentSuperAdmin,
):
    """Update a user (super-admin only)."""
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    update_data = user_data.model_dump(exclude_unset=True, exclude={"password"})
    if user_data.password:
        update_data["password_hash"] = get_password_hash(user_data.password)

    updated = await user_repo.update(user, update_data)
    return UserResponse.model_validate(updated)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: uuid.UUID,
    db: DbSession,
    current_admin: CurrentSuperAdmin,
):
    """Deactivate a user (super-admin only)."""
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate yourself",
        )

    await user_repo.delete(user)


@router.post("/{user_id}/activate", response_model=UserResponse)
async def activate_user(
    user_id: uuid.UUID,
    db: DbSession,
    current_admin: CurrentSuperAdmin,
):
    """Activate a deactivated user (super-admin only)."""
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    updated = await user_repo.update(user, {"is_active": True})
    return UserResponse.model_validate(updated)
