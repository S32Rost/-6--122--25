"""Data models."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class Student:
    """Student model."""
    id: int
    name: str
    age: int
    major: str
    enrolled_at: datetime

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "major": self.major,
            "enrolled_at": self.enrolled_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Student":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            age=data["age"],
            major=data["major"],
            enrolled_at=datetime.fromisoformat(data["enrolled_at"])
        )