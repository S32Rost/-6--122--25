"""Tests for JSON file-based database."""

import unittest
import os
import tempfile
from src.database.file_json import FileDatabaseJSON
from src.database.schemas import SCHEMAS
from src.database.errors import RecordNotFoundError, ValidationError, DatabaseError

class TestFileDatabaseJSON(unittest.TestCase):
    """Test FileDatabaseJSON class."""
    
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
        self.temp_file.close()
        self.db = FileDatabaseJSON(self.temp_file.name)
        self.db.create_table("students", SCHEMAS["students"])
    
    def tearDown(self):
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)
    
    def test_create_table(self):
        """Test table creation."""
        self.assertTrue(self.db.table_exists("students"))
    
    def test_insert_and_get(self):
        """Test insert and get by id."""
        record = self.db.insert("students", name="Тест", age=20, major="Тест", email="test@test.com")
        self.assertEqual(record["name"], "Тест")
        
        # Check persistence
        new_db = FileDatabaseJSON(self.temp_file.name)
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

    def test_corrupted_json_file_raises_error(self):
        """Test that corrupted JSON file raises DatabaseError."""
        temp_file = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
        temp_name = temp_file.name
        temp_file.close()
        
        # Записываем некорректный JSON
        with open(temp_name, 'w', encoding='utf-8') as f:
            f.write("this is not valid json {")
        
        with self.assertRaises(DatabaseError) as context:
            FileDatabaseJSON(temp_name)
        
        self.assertIn("повреждён", str(context.exception))
        os.unlink(temp_name)

if __name__ == "__main__":
    unittest.main()