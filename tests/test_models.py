"""Tests for data models."""

import unittest
from datetime import datetime
from src.database.models import Student


class TestStudent(unittest.TestCase):
    """Test Student model."""
    
    def setUp(self):
        self.now = datetime.now()
        self.student = Student(
            id=1,
            name="Иван Петров",
            age=20,
            major="Информатика",
            enrolled_at=self.now
        )
    
    def test_student_creation(self):
        self.assertEqual(self.student.id, 1)
        self.assertEqual(self.student.name, "Иван Петров")
        self.assertEqual(self.student.age, 20)
        self.assertEqual(self.student.major, "Информатика")
        self.assertEqual(self.student.enrolled_at, self.now)
    
    def test_to_dict(self):
        data = self.student.to_dict()
        self.assertEqual(data["id"], 1)
        self.assertEqual(data["name"], "Иван Петров")
        self.assertEqual(data["age"], 20)
        self.assertEqual(data["major"], "Информатика")
        self.assertEqual(data["enrolled_at"], self.now.isoformat())
    
    def test_from_dict(self):
        data = {
            "id": 2,
            "name": "Мария Сидорова",
            "age": 19,
            "major": "Математика",
            "enrolled_at": self.now.isoformat()
        }
        student = Student.from_dict(data)
        self.assertEqual(student.id, 2)
        self.assertEqual(student.name, "Мария Сидорова")
        self.assertEqual(student.age, 19)
        self.assertEqual(student.major, "Математика")
    
    def test_round_trip(self):
        data = self.student.to_dict()
        restored = Student.from_dict(data)
        self.assertEqual(self.student.id, restored.id)
        self.assertEqual(self.student.name, restored.name)
        self.assertEqual(self.student.age, restored.age)


if __name__ == "__main__":
    unittest.main()