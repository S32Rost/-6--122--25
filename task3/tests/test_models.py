import unittest
from datetime import datetime
from models import Student

class TestStudent(unittest.TestCase):
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
    
    def test_from_dict_and_back(self):
        original = self.student
        data = original.to_dict()
        restored = Student.from_dict(data)
        self.assertEqual(original.id, restored.id)
        self.assertEqual(original.name, restored.name)
        self.assertEqual(original.age, restored.age)
        self.assertEqual(original.major, restored.major)


if __name__ == "__main__":
    unittest.main()