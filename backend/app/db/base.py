"""Base database model."""
from typing import Any
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all models."""

    def __repr__(self) -> str:
        """String representation of the model."""
        return f"<{self.__class__.__name__} {getattr(self, 'id', None)}>"
