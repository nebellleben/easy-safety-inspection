"""Authentication API endpoints."""
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser, DbSession
from app.core.security import create_access_token, verify_password, get_password_hash
from app.repositories.user import UserRepository
from app.schemas.user import LoginRequest, LoginResponse, UserResponse

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(
    credentials: LoginRequest,
    db: DbSession,
):
    """Login with staff ID and password (for admin users)."""
    user_repo = UserRepository(db)
    user = await user_repo.get_by_staff_id(credentials.staff_id)

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Check if user has a password (admin users)
    if not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please use the Telegram bot to register first",
        )

    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    access_token = create_access_token(
        subject=str(user.id),
        expires_delta=timedelta(minutes=60 * 24 * 7),  # 7 days
    )

    return LoginResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: CurrentUser,
):
    """Get current user info."""
    return UserResponse.model_validate(current_user)


@router.post("/refresh")
async def refresh_token():
    """Refresh access token."""
    # JWT is long-lived (7 days), so this endpoint can be used
    # to validate token and get user info
    # Implementation depends on the auth strategy
    return {"message": "Token is valid"}


@router.post("/logout")
async def logout():
    """Logout user."""
    # For JWT-based auth, logout is handled client-side
    # by deleting the token
    return {"message": "Successfully logged out"}
