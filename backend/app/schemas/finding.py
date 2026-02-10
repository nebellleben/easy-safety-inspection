"""Finding schemas."""
import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class Severity(str, Enum):
    """Finding severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Status(str, Enum):
    """Finding status values."""

    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class SeverityLabel(str, Enum):
    """Severity labels for display."""

    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class StatusLabel(str, Enum):
    """Status labels for display."""

    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"
    CLOSED = "Closed"


class StatusHistoryEntry(BaseModel):
    """Status history entry schema."""

    id: uuid.UUID
    old_status: str | None
    new_status: str
    notes: str | None
    updated_by: uuid.UUID
    updated_at: datetime

    model_config = {"from_attributes": True}


class Photo(BaseModel):
    """Photo schema."""

    id: uuid.UUID
    finding_id: uuid.UUID
    s3_key: str
    original_filename: str
    mime_type: str
    size: int
    uploaded_at: datetime

    model_config = {"from_attributes": True}


class FindingBase(BaseModel):
    """Base finding schema."""

    description: str = Field(..., min_length=1, max_length=5000)
    severity: Severity = Severity.MEDIUM
    location: str | None = Field(None, max_length=500)


class FindingCreate(FindingBase):
    """Finding creation schema."""

    area_id: uuid.UUID
    reporter_telegram_id: int | None = None


class FindingUpdate(BaseModel):
    """Finding update schema."""

    description: str | None = Field(None, min_length=1, max_length=5000)
    severity: Severity | None = None
    location: str | None = None
    assigned_to: uuid.UUID | None = None


class FindingStatusUpdate(BaseModel):
    """Finding status update schema."""

    status: Status
    notes: str | None = Field(None, max_length=2000)


# Import schemas to avoid circular imports
# These will be imported properly in the module
class UserRef(BaseModel):
    """Minimal user reference schema."""

    id: uuid.UUID
    full_name: str
    staff_id: str
    department: str
    section: str
    role: str

    model_config = {"from_attributes": True}


class AreaRef(BaseModel):
    """Minimal area reference schema."""

    id: uuid.UUID
    name: str
    full_path: str | None = None
    level: int

    model_config = {"from_attributes": True}


class FindingResponse(FindingBase):
    """Finding response schema."""

    id: uuid.UUID
    report_id: str
    reporter_id: uuid.UUID
    area_id: uuid.UUID
    status: Status
    reported_at: datetime
    closed_at: datetime | None
    assigned_to: uuid.UUID | None
    created_at: datetime
    updated_at: datetime

    # Nested relations
    reporter: UserRef | None = None
    assignee: UserRef | None = None
    area: AreaRef | None = None
    photos: list[Photo] = []
    status_history: list[StatusHistoryEntry] = []

    model_config = {"from_attributes": True}


class FindingListResponse(BaseModel):
    """Finding list response schema."""

    items: list[FindingResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class FindingSummary(BaseModel):
    """Finding summary for reports."""

    severity: Severity
    count: int
    percentage: float


class AreaSummary(BaseModel):
    """Area summary for reports."""

    area_name: str
    total_findings: int
    open_findings: int
    closed_findings: int
    by_severity: dict[str, int]


class SummaryReport(BaseModel):
    """Summary report response."""

    date_from: datetime
    date_to: datetime
    total_findings: int
    by_severity: list[FindingSummary]
    by_status: dict[str, int]
    by_area: list[AreaSummary]
