"""Notification settings API endpoints."""
from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.deps import CurrentUser

router = APIRouter()


class NotificationType(str, Enum):
    """Notification types."""

    NEW_FINDING = "new_finding"
    STATUS_CHANGE = "status_change"
    DAILY_SUMMARY = "daily_summary"
    WEEKLY_SUMMARY = "weekly_summary"


class NotificationSettings(BaseModel):
    """Notification settings model."""

    new_finding: bool = True
    status_change: bool = True
    daily_summary: bool = True
    weekly_summary: bool = True
    daily_summary_time: str = "09:00"


@router.get("/settings", response_model=NotificationSettings)
async def get_notification_settings(
    current_user: CurrentUser,
):
    """Get user's notification preferences."""
    # TODO: Implement notification settings from database
    return NotificationSettings()


@router.patch("/settings", response_model=NotificationSettings)
async def update_notification_settings(
    settings: NotificationSettings,
    current_user: CurrentUser,
):
    """Update user's notification preferences."""
    # TODO: Implement notification settings update
    return settings


@router.post("/test")
async def send_test_notification(
    current_user: CurrentUser,
):
    """Send a test notification to the user."""
    # TODO: Implement test notification via Telegram
    if not current_user.telegram_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No Telegram account linked",
        )

    return {"message": "Test notification sent"}
