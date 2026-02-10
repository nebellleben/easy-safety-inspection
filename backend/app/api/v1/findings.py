"""Findings API endpoints."""
import uuid
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentAdmin, CurrentUser, DbSession
from app.models.finding import Severity, Status
from app.repositories.finding import FindingRepository
from app.repositories.user import UserRepository
from app.schemas.finding import (
    FindingCreate,
    FindingListResponse,
    FindingResponse,
    FindingStatusUpdate,
    SummaryReport,
)

router = APIRouter()


@router.get("", response_model=FindingListResponse)
async def list_findings(
    db: DbSession,
    current_user: CurrentUser,
    area_id: uuid.UUID | None = None,
    severity: Severity | None = None,
    status: Status | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    """List findings with optional filtering."""
    finding_repo = FindingRepository(db)

    # Non-super-admins can only see findings from their assigned areas
    # For now, allow all admins to see all findings
    # TODO: Implement area-based filtering

    offset = (page - 1) * page_size
    findings, total = await finding_repo.list_findings(
        area_id=area_id,
        severity=severity,
        status=status,
        date_from=date_from,
        date_to=date_to,
        offset=offset,
        limit=page_size,
    )

    total_pages = (total + page_size - 1) // page_size

    return FindingListResponse(
        items=[FindingResponse.model_validate(f) for f in findings],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{finding_id}", response_model=FindingResponse)
async def get_finding(
    finding_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
):
    """Get finding details."""
    finding_repo = FindingRepository(db)
    finding = await finding_repo.get_by_id(finding_id)

    if not finding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Finding not found",
        )

    # TODO: Check area access for non-super-admins

    return FindingResponse.model_validate(finding)


@router.patch("/{finding_id}/status", response_model=FindingResponse)
async def update_finding_status(
    finding_id: uuid.UUID,
    status_update: FindingStatusUpdate,
    db: DbSession,
    current_user: CurrentAdmin,
):
    """Update finding status."""
    finding_repo = FindingRepository(db)
    finding = await finding_repo.get_by_id(finding_id)

    if not finding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Finding not found",
        )

    # TODO: Check area access

    await finding_repo.update_status(
        finding, status_update.status, current_user.id, status_update.notes
    )

    return FindingResponse.model_validate(finding)


@router.patch("/{finding_id}/assign", response_model=FindingResponse)
async def assign_finding(
    finding_id: uuid.UUID,
    current_user: CurrentAdmin,
    db: DbSession,
    assigned_to: uuid.UUID | None = None,
):
    """Assign finding to a user."""
    finding_repo = FindingRepository(db)
    user_repo = UserRepository(db)

    finding = await finding_repo.get_by_id(finding_id)
    if not finding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Finding not found",
        )

    if assigned_to:
        user = await user_repo.get_by_id(assigned_to)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

    await finding_repo.assign(finding, assigned_to)

    return FindingResponse.model_validate(finding)


@router.post("/summary", response_model=SummaryReport)
async def generate_summary(
    current_user: CurrentAdmin,
    db: DbSession,
    date_from: Annotated[datetime, Query()] = ...,
    date_to: Annotated[datetime | None, Query()] = None,
):
    """Generate summary report for a date range."""
    if not date_to:
        date_to = datetime.now(timezone.utc)

    finding_repo = FindingRepository(db)
    findings, total = await finding_repo.list_findings(
        date_from=date_from,
        date_to=date_to,
        offset=0,
        limit=10000,  # Large limit for reports
    )

    # Calculate summary statistics
    severity_counts = {}
    status_counts = {}
    area_counts = {}

    for f in findings:
        severity_counts[f.severity] = severity_counts.get(f.severity, 0) + 1
        status_counts[f.status] = status_counts.get(f.status, 0) + 1
        # Area statistics would be calculated here

    # Build response
    from app.schemas.finding import FindingSummary, AreaSummary

    by_severity = [
        FindingSummary(
            severity=sev,
            count=count,
            percentage=round((count / total * 100) if total > 0 else 0, 2),
        )
        for sev, count in severity_counts.items()
    ]

    by_area = []  # TODO: Implement area-based aggregation

    return SummaryReport(
        date_from=date_from,
        date_to=date_to,
        total_findings=total,
        by_severity=by_severity,
        by_status=status_counts,
        by_area=by_area,
    )
