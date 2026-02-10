"""Areas API endpoints."""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentAdmin, CurrentSuperAdmin, CurrentUser, DbSession
from app.repositories.area import AreaRepository
from app.schemas.area import AreaCreate, AreaResponse, AreaUpdate

router = APIRouter()


@router.get("", response_model=list[AreaResponse])
async def list_areas(
    db: DbSession,
    current_user: CurrentUser,
    level: int | None = Query(None, ge=1, le=3),
    parent_id: uuid.UUID | None = None,
):
    """List areas with optional filtering."""
    area_repo = AreaRepository(db)
    areas = await area_repo.list_areas(level=level, parent_id=parent_id)
    return [AreaResponse.model_validate(a) for a in areas]


@router.get("/tree", response_model=list[AreaResponse])
async def get_area_tree(
    db: DbSession,
    current_user: CurrentUser,
):
    """Get areas as a tree structure."""
    area_repo = AreaRepository(db)
    areas = await area_repo.get_tree()
    return [AreaResponse.model_validate(a) for a in areas]


@router.get("/{area_id}", response_model=AreaResponse)
async def get_area(
    area_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
):
    """Get area details."""
    area_repo = AreaRepository(db)
    area = await area_repo.get_by_id(area_id)

    if not area:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Area not found",
        )

    return AreaResponse.model_validate(area)


@router.post("", response_model=AreaResponse, status_code=status.HTTP_201_CREATED)
async def create_area(
    area_data: AreaCreate,
    db: DbSession,
    current_user: CurrentSuperAdmin,
):
    """Create a new area (super-admin only)."""
    area_repo = AreaRepository(db)

    # Check if area with same name exists
    existing = await area_repo.get_by_name(area_data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Area with this name already exists",
        )

    # Validate parent exists if specified
    if area_data.parent_id:
        parent = await area_repo.get_by_id(area_data.parent_id)
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent area not found",
            )
        # Set level based on parent
        area_data.level = parent.level + 1
        if area_data.level > 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot create area deeper than 3 levels",
            )

    area = await area_repo.create(area_data.model_dump())
    return AreaResponse.model_validate(area)


@router.patch("/{area_id}", response_model=AreaResponse)
async def update_area(
    area_id: uuid.UUID,
    area_data: AreaUpdate,
    db: DbSession,
    current_user: CurrentSuperAdmin,
):
    """Update an area (super-admin only)."""
    area_repo = AreaRepository(db)
    area = await area_repo.get_by_id(area_id)

    if not area:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Area not found",
        )

    updated = await area_repo.update(area, area_data.model_dump(exclude_unset=True))
    return AreaResponse.model_validate(updated)


@router.delete("/{area_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_area(
    area_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentSuperAdmin,
):
    """Delete an area (super-admin only)."""
    area_repo = AreaRepository(db)
    area = await area_repo.get_by_id(area_id)

    if not area:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Area not found",
        )

    # Check if area has children
    if area.children:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete area with child areas. Delete children first.",
        )

    await area_repo.delete(area)


@router.post("/{area_id}/admins")
async def assign_admin_to_area(
    area_id: uuid.UUID,
    user_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentSuperAdmin,
):
    """Assign an admin to an area (super-admin only)."""
    # TODO: Implement user_areas junction table
    return {"message": "Admin assigned to area"}
