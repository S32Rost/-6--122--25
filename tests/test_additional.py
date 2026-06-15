"""Additional tests to increase coverage."""

import unittest
import tempfile
import os
from src.database.in_memory import InMemoryDatabase
from src.database.file_json import FileDatabaseJSON
from src.database.file_csv import FileDatabaseCSV
from src.database.schemas import SCHEMAS
from src.database.errors import DatabaseError, RecordNotFoundError, ValidationError


class TestAdditionalCoverage(unittest.TestCase):
    """Additional tests for better coverage."""
    
    def setUp(self):
        self.db = InMemoryDatabase("test_db")
        self.db.create_table("students", SCHEMAS["students"])
        self.db.insert("students", name="Тест", age=20, major="Тест", email="test@test.com")
    
    # ========== InMemoryDatabase дополнительные тесты ==========
    def test_in_memory_delete_nonexistent_table(self):
        with self.assertRaises(DatabaseError):
            self.db.delete("nonexistent", 1)
    
    def test_in_memory_update_nonexistent_table(self):
        with self.assertRaises(DatabaseError):
            self.db.update("nonexistent", 1, name="Новое")
    
    def test_in_memory_get_all_nonexistent_table(self):
        with self.assertRaises(DatabaseError):
            self.db.get_all("nonexistent")
    
    def test_in_memory_filter_nonexistent_table(self):
        with self.assertRaises(DatabaseError):
            self.db.filter("nonexistent", {"name": "Тест"})
    
    def test_in_memory_sort_invalid_field(self):
        with self.assertRaises(ValidationError):
            self.db.sort("students", "nonexistent_field")
    
    # ========== FileDatabaseJSON дополнительные тесты ==========
    def test_json_create_duplicate_table(self):
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            f.close()
            db = FileDatabaseJSON(f.name)
            db.create_table("test", {"name": str})
            with self.assertRaises(DatabaseError):
                db.create_table("test", {"name": str})
            os.unlink(f.name)
    
    def test_json_insert_invalid_data(self):
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            f.close()
            db = FileDatabaseJSON(f.name)
            db.create_table("test", {"name": str, "age": int})
            with self.assertRaises(ValidationError):
                db.insert("test", name="Тест")
            os.unlink(f.name)
    
    def test_json_update_invalid_field_type(self):
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            f.close()
            db = FileDatabaseJSON(f.name)
            db.create_table("test", {"name": str, "age": int})
            db.insert("test", name="Тест", age=20)
            with self.assertRaises(ValidationError):
                db.update("test", 1, age="двадцать")
            os.unlink(f.name)
    
    def test_json_filter_invalid_operator(self):
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            f.close()
            db = FileDatabaseJSON(f.name)
            db.create_table("test", {"name": str, "age": int})
            db.insert("test", name="Тест", age=20)
            with self.assertRaises(ValidationError):
                db.filter("test", {"age__invalid": 20})
            os.unlink(f.name)
    
    def test_json_drop_nonexistent_table(self):
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            f.close()
            db = FileDatabaseJSON(f.name)
            with self.assertRaises(DatabaseError):
                db.drop_table("nonexistent")
            os.unlink(f.name)
    
    # ========== FileDatabaseCSV дополнительные тесты ==========
    def test_csv_create_duplicate_table(self):
        import tempfile
        import shutil
        temp_dir = tempfile.mkdtemp()
        db = FileDatabaseCSV(temp_dir)
        db.create_table("test", {"name": str})
        with self.assertRaises(DatabaseError):
            db.create_table("test", {"name": str})
        shutil.rmtree(temp_dir)
    
    def test_csv_insert_invalid_data(self):
        import tempfile
        import shutil
        temp_dir = tempfile.mkdtemp()
        db = FileDatabaseCSV(temp_dir)
        db.create_table("test", {"name": str, "age": int})
        with self.assertRaises(ValidationError):
            db.insert("test", name="Тест")
        shutil.rmtree(temp_dir)
    
    def test_csv_update_invalid_field_type(self):
        import tempfile
        import shutil
        temp_dir = tempfile.mkdtemp()
        db = FileDatabaseCSV(temp_dir)
        db.create_table("test", {"name": str, "age": int})
        db.insert("test", name="Тест", age=20)
        with self.assertRaises(ValidationError):
            db.update("test", 1, age="двадцать")
        shutil.rmtree(temp_dir)
    
    def test_csv_filter_invalid_operator(self):
        import tempfile
        import shutil
        temp_dir = tempfile.mkdtemp()
        db = FileDatabaseCSV(temp_dir)
        db.create_table("test", {"name": str, "age": int})
        db.insert("test", name="Тест", age=20)
        with self.assertRaises(ValidationError):
            db.filter("test", {"age__invalid": 20})
        shutil.rmtree(temp_dir)
    
    def test_csv_drop_nonexistent_table(self):
        import tempfile
        import shutil
        temp_dir = tempfile.mkdtemp()
        db = FileDatabaseCSV(temp_dir)
        with self.assertRaises(DatabaseError):
            db.drop_table("nonexistent")
        shutil.rmtree(temp_dir)
    
    def test_csv_sort_nonexistent_table(self):
        import tempfile
        import shutil
        temp_dir = tempfile.mkdtemp()
        db = FileDatabaseCSV(temp_dir)
        with self.assertRaises(DatabaseError):
            db.sort("nonexistent", "name")
        shutil.rmtree(temp_dir)
    
    # ========== Тесты для ошибок ==========
    def test_database_error_str(self):
        error = DatabaseError("Тест ошибки")
        self.assertEqual(str(error), "Тест ошибки")
    
    def test_record_not_found_error_str(self):
        error = RecordNotFoundError("Запись не найдена")
        self.assertEqual(str(error), "Запись не найдена")


if __name__ == "__main__":
    unittest.main()