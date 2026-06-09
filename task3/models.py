from dataclasses import dataclass
from datetime import datetime
from typing import Any

@dataclass
class Student:
    id: int
    name: str
    age: int
    major: str
    enrolled_at: datetime

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "major": self.major,
            "enrolled_at": self.enrolled_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Student":
        return cls(
            id=data["id"],
            name=data["name"],
            age=data["age"],
            major=data["major"],
            enrolled_at=datetime.fromisoformat(data["enrolled_at"])
        )