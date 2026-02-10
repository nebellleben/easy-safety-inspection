"""Area model."""
import uuid
from datetime import datetime, timezone
from typing import Self

from sqlalchemy import DateTime, String, Text, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Area(Base):
    """Area model with hierarchical support (2-3 levels)."""

    __tablename__ = "areas"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("areas.id", ondelete="CASCADE"), nullable=True, index=True
    )
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # 1, 2, or 3
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Self-referential relationship for hierarchy
    parent: Mapped[Self | None] = relationship(
        "Area",
        remote_side=[id],
        backref="children",
    )

    def __repr__(self) -> str:
        return f"<Area {self.name} (Level {self.level})>"

    @property
    def full_path(self) -> str:
        """Get full path including parent areas."""
        if self.parent:
            return f"{self.parent.full_path} > {self.name}"
        return self.name

    def get_descendants(self, include_self: bool = False) -> list["Area"]:
        """Get all descendant areas."""
        # This would need to be implemented with a recursive CTE query
        # For now, returning empty list
        return [self] if include_self else []
