"""Tests for CSV file-based database."""

import unittest
import tempfile
import shutil
from src.database.file_csv import FileDatabaseCSV
from src.database.schemas import SCHEMAS
from src.database.errors import RecordNotFoundError, ValidationError, DatabaseError

class TestFileDatabaseCSV(unittest.TestCase):
    """Test FileDatabaseCSV class."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db = FileDatabaseCSV(self.temp_dir)
        self.db.create_table("students", SCHEMAS["students"])
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_create_table(self):
        """Test table creation."""
        self.assertTrue(self.db.table_exists("students"))
    
    def test_insert_and_get(self):
        """Test insert and get by id."""
        record = self.db.insert("students", name="Тест", age=20, major="Тест", email="test@test.com")
        self.assertEqual(record["name"], "Тест")
        
        # Check persistence
        new_db = FileDatabaseCSV(self.temp_dir)
        loaded = new_db.get_by_id("students", 1)
        self.assertEqual(loaded["name"], "Тест")
    
    def test_get_all(self):
        """Test get all records."""
        self.db.insert("students", name="Иван", age=20, major="Информатика", email="i@i.com")
        self.db.insert("students", name="Петр", age=25, major="Физика", email="p@p.com")
        records = self.db.get_all("students")
        self.assertEqual(len(records), 2)
    
    def test_update(self):
        """Test update record."""
        self.db.insert("students", name="Старый", age=20, major="Тест", email="test@test.com")
        updated = self.db.update("students", 1, name="Новый", age=21)
        self.assertEqual(updated["name"], "Новый")
        self.assertEqual(updated["age"], 21)
    
    def test_delete(self):
        """Test delete record."""
        self.db.insert("students", name="Тест", age=20, major="Тест", email="test@test.com")
        self.db.delete("students", 1)
        with self.assertRaises(RecordNotFoundError):
            self.db.get_by_id("students", 1)
    
    def test_filter(self):
        """Test filter records."""
        self.db.insert("students", name="Иван", age=20, major="Информатика", email="i@i.com")
        self.db.insert("students", name="Петр", age=25, major="Физика", email="p@p.com")
        results = self.db.filter("students", {"age__gt": 22})
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Петр")
    
    def test_sort(self):
        """Test sort records."""
        self.db.insert("students", name="Иван", age=20, major="Информатика", email="i@i.com")
        self.db.insert("students", name="Анна", age=22, major="Физика", email="a@a.com")
        self.db.insert("students", name="Борис", age=21, major="Мат", email="b@b.com")
        
        results = self.db.sort("students", "name", reverse=False)
        names = [r["name"] for r in results]
        self.assertEqual(names, ["Анна", "Борис", "Иван"])

    def test_insert_with_extra_field_rejected(self):
        """Test insert with extra field should raise ValidationError."""
        with self.assertRaises(ValidationError):
            self.db.insert(
                "students",
                name="Иван",
                age=20,
                major="Информатика",
                email="ivan@test.com",
                extra_field="should_be_rejected"
            )
    
    def test_update_with_extra_field_rejected(self):
        """Test update with extra field should raise ValidationError."""
        self.db.insert(
            "students",
            name="Иван",
            age=20,
            major="Информатика",
            email="ivan@test.com"
        )
        with self.assertRaises(ValidationError):
            self.db.update("students", 1, extra_field="should_be_rejected")

if __name__ == "__main__":
    unittest.main()
