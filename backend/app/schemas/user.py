"""User schemas."""
import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field, field_validator


class Role(str, Enum):
    """User roles."""

    REPORTER = "reporter"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class UserBase(BaseModel):
    """Base user schema."""

    full_name: str = Field(..., min_length=1, max_length=255)
    staff_id: str = Field(..., min_length=1, max_length=50)
    department: str = Field(..., min_length=1, max_length=100)
    section: str = Field(..., min_length=1, max_length=100)
    role: Role = Role.REPORTER


class UserCreate(UserBase):
    """User creation schema."""

    telegram_id: int | None = None
    username: str | None = None
    password: str | None = Field(None, min_length=8)
    is_active: bool = True

    @field_validator("password")
    @classmethod
    def validate_admin_password(cls, v: str | None, info) -> str | None:
        """Validate that admin users have a password."""
        if info.data.get("role") in (Role.ADMIN, Role.SUPER_ADMIN) and not v:
            raise ValueError("Password is required for admin users")
        return v


class UserUpdate(BaseModel):
    """User update schema."""

    full_name: str | None = None
    department: str | None = None
    section: str | None = None
    role: Role | None = None
    is_active: bool | None = None
    password: str | None = Field(None, min_length=8)


class UserResponse(UserBase):
    """User response schema."""

    id: uuid.UUID
    telegram_id: int | None
    username: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    """Login request schema."""

    staff_id: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class LoginResponse(BaseModel):
    """Login response schema."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TelegramAuth(BaseModel):
    """Telegram auth data from bot."""

    telegram_id: int
    username: str | None = None
    full_name: str
    staff_id: str
    department: str
    section: str
