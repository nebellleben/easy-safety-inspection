"""Area schemas."""
import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class AreaBase(BaseModel):
    """Base area schema."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    parent_id: uuid.UUID | None = None
    level: int = Field(default=1, ge=1, le=3)


class AreaCreate(AreaBase):
    """Area creation schema."""

    pass


class AreaUpdate(BaseModel):
    """Area update schema."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    parent_id: uuid.UUID | None = None


class AreaResponse(AreaBase):
    """Area response schema."""

    id: uuid.UUID
    created_at: datetime
    full_path: str | None = None
    children: list["AreaResponse"] = []

    model_config = {"from_attributes": True}


# Enable forward references
AreaResponse.model_rebuild()
