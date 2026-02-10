"""Finding repository."""
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.finding import Finding, Severity, Status
from app.models.status_history import StatusHistory


class FindingRepository:
    """Repository for Finding model operations."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize repository."""
        self.db = db

    async def get_by_id(self, finding_id: str | uuid.UUID) -> Finding | None:
        """Get finding by ID with all relations."""
        if isinstance(finding_id, str):
            finding_id = uuid.UUID(finding_id)
        result = await self.db.execute(
            select(Finding)
            .options(
                selectinload(Finding.reporter),
                selectinload(Finding.assignee),
                selectinload(Finding.area),
                selectinload(Finding.photos),
                selectinload(Finding.status_history),
            )
            .where(Finding.id == finding_id)
        )
        return result.scalar_one_or_none()

    async def get_by_report_id(self, report_id: str) -> Finding | None:
        """Get finding by report ID."""
        result = await self.db.execute(
            select(Finding)
            .options(
                selectinload(Finding.reporter),
                selectinload(Finding.assignee),
                selectinload(Finding.area),
                selectinload(Finding.photos),
                selectinload(Finding.status_history),
            )
            .where(Finding.report_id == report_id)
        )
        return result.scalar_one_or_none()

    async def list_findings(
        self,
        area_id: uuid.UUID | None = None,
        severity: Severity | None = None,
        status: Status | None = None,
        reporter_id: uuid.UUID | None = None,
        assigned_to: uuid.UUID | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[Finding], int]:
        """List findings with optional filtering."""
        query = select(Finding).options(
            selectinload(Finding.reporter),
            selectinload(Finding.assignee),
            selectinload(Finding.area),
            selectinload(Finding.photos),
            selectinload(Finding.status_history).selectinload(StatusHistory.updated_by_user),
        )

        # Build filters
        filters = []
        if area_id:
            # Include child areas if hierarchical
            filters.append(Finding.area_id == area_id)
        if severity:
            filters.append(Finding.severity == severity)
        if status:
            filters.append(Finding.status == status)
        if reporter_id:
            filters.append(Finding.reporter_id == reporter_id)
        if assigned_to:
            filters.append(Finding.assigned_to == assigned_to)
        if date_from:
            filters.append(Finding.reported_at >= date_from)
        if date_to:
            filters.append(Finding.reported_at <= date_to)

        if filters:
            query = query.where(and_(*filters))

        # Get total count
        count_query = select(Finding.id)
        if filters:
            count_query = count_query.where(and_(*filters))
        count_result = await self.db.execute(count_query)
        total = len(count_result.all())

        # Get paginated results
        query = query.offset(offset).limit(limit).order_by(desc(Finding.reported_at))
        result = await self.db.execute(query)
        findings = list(result.scalars().all())

        return findings, total

    async def create(self, finding_data: dict[str, Any]) -> Finding:
        """Create a new finding."""
        finding = Finding(**finding_data)
        self.db.add(finding)
        await self.db.flush()

        # Add initial status history
        history = StatusHistory(
            finding_id=finding.id,
            old_status=None,
            new_status=finding.status,
            notes="Finding created",
            updated_by=finding.reporter_id,
        )
        self.db.add(history)
        await self.db.flush()

        return finding

    async def update_status(
        self,
        finding: Finding,
        new_status: Status,
        updated_by: uuid.UUID,
        notes: str | None = None,
    ) -> Finding:
        """Update finding status."""
        old_status = finding.status
        finding.status = new_status

        if new_status == Status.CLOSED:
            finding.closed_at = datetime.now(timezone.utc)

        # Add status history
        history = StatusHistory(
            finding_id=finding.id,
            old_status=old_status,
            new_status=new_status,
            notes=notes,
            updated_by=updated_by,
        )
        self.db.add(history)
        await self.db.flush()

        return finding

    async def assign(self, finding: Finding, assigned_to: uuid.UUID | None) -> Finding:
        """Assign finding to a user."""
        finding.assigned_to = assigned_to
        await self.db.flush()
        return finding

    def generate_report_id(self, year: int) -> str:
        """Generate a unique report ID."""
        # This should query for the highest sequential number in the year
        # For now, return a placeholder
        return f"SF-{year:04d}-0001"

    async def get_next_report_id(self) -> str:
        """Get the next sequential report ID."""
        year = datetime.now().year
        prefix = f"SF-{year:04d}-"

        # Find the highest sequential number for this year
        result = await self.db.execute(
            select(Finding.report_id)
            .where(Finding.report_id.like(prefix))
            .order_by(desc(Finding.report_id))
            .limit(1)
        )
        last_id = result.scalar_one_or_none()

        if last_id:
            # Extract and increment the sequential number
            try:
                last_seq = int(last_id.split("-")[-1])
                next_seq = last_seq + 1
            except (ValueError, IndexError):
                next_seq = 1
        else:
            next_seq = 1

        return f"{prefix}{next_seq:04d}"
