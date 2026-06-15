"""Additional tests to boost coverage to 80%."""

import unittest
import tempfile
import os
import shutil
from src.database.validators import (
    validate_student_data,
    validate_book_data,
    validate_employee_data,
    validate_record
)
from src.database.errors import ValidationError, DatabaseError
from src.database.schemas import SCHEMAS
from src.database.file_json import FileDatabaseJSON
from src.database.file_csv import FileDatabaseCSV
from src.database.in_memory import InMemoryDatabase


class TestCoverageBoost(unittest.TestCase):
    """Tests to increase coverage."""
    
    # ========== Для validators.py ==========
    
    def test_student_name_edge_cases(self):
        """Test student name edge cases."""
        validate_student_data("Иван-Петр", 20, "Информатика", "test@test.com")
        validate_student_data("Anna Maria", 20, "Информатика", "test@test.com")
    
    def test_student_age_boundaries(self):
        """Test student age boundaries."""
        validate_student_data("Иван", 16, "Информатика", "test@test.com")
        validate_student_data("Иван", 120, "Информатика", "test@test.com")
    
    def test_student_invalid_age_string(self):
        """Test student age with string."""
        with self.assertRaises(ValidationError):
            validate_student_data("Иван", "двадцать", "Информатика", "test@test.com")
    
    def test_student_with_email(self):
        """Test student with email."""
        try:
            validate_student_data("Иван", 20, "Информатика", "ivan@test.com")
        except ValidationError:
            self.fail("Valid student data should pass")
    
    def test_book_year_boundaries(self):
        """Test book year boundaries."""
        validate_book_data("Книга", "Автор", 1450, "1234567890")
        from datetime import datetime
        current_year = datetime.now().year
        validate_book_data("Книга", "Автор", current_year + 5, "1234567890")
    
    def test_book_year_invalid(self):
        """Test book year invalid."""
        with self.assertRaises(ValidationError):
            validate_book_data("Книга", "Автор", "тысяча", "1234567890")
    
    def test_book_isbn_with_spaces(self):
        """Test ISBN with spaces."""
        validate_book_data("Книга", "Автор", 2020, "978 5 17 113922 7")
    
    def test_book_isbn_with_dashes(self):
        """Test ISBN with dashes."""
        validate_book_data("Книга", "Автор", 2020, "978-5-17-113922-7")
    
    def test_employee_salary_float(self):
        """Test employee salary as float."""
        validate_employee_data("Иван Иванов", "Программист", 100000.50, "IT")
    
    def test_employee_salary_int(self):
        """Test employee salary as int."""
        validate_employee_data("Иван Иванов", "Программист", 100000, "IT")
    
    # ========== Для file_csv.py ==========
    
    def test_csv_load_empty_file(self):
        """Test loading empty CSV file."""
        temp_dir = tempfile.mkdtemp()
        db = FileDatabaseCSV(temp_dir)
        db.create_table("test", {"name": str})
        shutil.rmtree(temp_dir)
    
    def test_csv_filter_contains(self):
        """Test CSV filter with contains."""
        temp_dir = tempfile.mkdtemp()
        db = FileDatabaseCSV(temp_dir)
        db.create_table("test", {"name": str, "age": int})
        db.insert("test", name="Alice", age=25)
        db.insert("test", name="Bob", age=30)
        db.insert("test", name="Charlie", age=35)
        
        results = db.filter("test", {"name__contains": "li"})
        self.assertEqual(len(results), 2)
        shutil.rmtree(temp_dir)
    
    def test_csv_filter_startswith(self):
        """Test CSV filter with startswith."""
        temp_dir = tempfile.mkdtemp()
        db = FileDatabaseCSV(temp_dir)
        db.create_table("test", {"name": str})
        db.insert("test", name="Apple")
        db.insert("test", name="Banana")
        
        results = db.filter("test", {"name__startswith": "Ap"})
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Apple")
        shutil.rmtree(temp_dir)
    
    def test_csv_delete_all_records(self):
        """Test CSV delete all records."""
        temp_dir = tempfile.mkdtemp()
        db = FileDatabaseCSV(temp_dir)
        db.create_table("test", {"name": str})
        db.insert("test", name="Record1")
        db.insert("test", name="Record2")
        
        self.assertEqual(len(db.get_all("test")), 2)
        db.delete("test", 1)
        db.delete("test", 2)
        self.assertEqual(len(db.get_all("test")), 0)
        shutil.rmtree(temp_dir)
    
    def test_csv_table_not_exists(self):
        """Test CSV operations on non-existent table."""
        temp_dir = tempfile.mkdtemp()
        db = FileDatabaseCSV(temp_dir)
        
        with self.assertRaises(DatabaseError):
            db.get_all("nonexistent")
        
        with self.assertRaises(DatabaseError):
            db.filter("nonexistent", {})
        
        shutil.rmtree(temp_dir)
    
    # ========== Для file_json.py ==========
    
    def test_json_load_empty_file(self):
        """Test loading empty JSON file."""
        temp_file = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
        temp_name = temp_file.name
        temp_file.close()
        db = FileDatabaseJSON(temp_name)
        db.create_table("test", {"name": str})
        self.assertTrue(db.table_exists("test"))
        os.unlink(temp_name)
    
    def test_json_filter_contains(self):
        """Test JSON filter with contains."""
        temp_file = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
        temp_name = temp_file.name
        temp_file.close()
        db = FileDatabaseJSON(temp_name)
        db.create_table("test", {"name": str})
        db.insert("test", name="Apple")
        db.insert("test", name="Banana")
        
        results = db.filter("test", {"name__contains": "pp"})
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Apple")
        os.unlink(temp_name)
    
    def test_json_filter_startswith(self):
        """Test JSON filter with startswith."""
        temp_file = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
        temp_name = temp_file.name
        temp_file.close()
        db = FileDatabaseJSON(temp_name)
        db.create_table("test", {"name": str})
        db.insert("test", name="Apple")
        db.insert("test", name="Banana")
        
        results = db.filter("test", {"name__startswith": "Ba"})
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Banana")
        os.unlink(temp_name)
    
    def test_json_table_not_exists(self):
        """Test JSON operations on non-existent table."""
        temp_file = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
        temp_name = temp_file.name
        temp_file.close()
        db = FileDatabaseJSON(temp_name)
        
        with self.assertRaises(DatabaseError):
            db.get_all("nonexistent")
        
        os.unlink(temp_name)
    
    # ========== Для in_memory.py ==========
    
    def test_in_memory_filter_startswith(self):
        """Test in-memory filter with startswith."""
        db = InMemoryDatabase("test")
        db.create_table("test", {"name": str})
        db.insert("test", name="Apple")
        db.insert("test", name="Banana")
        
        results = db.filter("test", {"name__startswith": "Ap"})
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Apple")
    
    def test_in_memory_filter_invalid_operator(self):
        """Test in-memory filter with invalid operator."""
        db = InMemoryDatabase("test")
        db.create_table("test", {"name": str})
        db.insert("test", name="Apple")
        
        with self.assertRaises(ValidationError):
            db.filter("test", {"name__invalid": "Apple"})
    
    def test_in_memory_sort_nonexistent_field(self):
        """Test in-memory sort with nonexistent field."""
        db = InMemoryDatabase("test")
        db.create_table("test", {"name": str})
        db.insert("test", name="Apple")
        
        with self.assertRaises(ValidationError):
            db.sort("test", "nonexistent_field")
    
    # ========== Для интерфейсов ==========
    
    def test_interface_abstract_methods_in_in_memory(self):
        """Test that InMemoryDatabase has all abstract methods."""
        db = InMemoryDatabase("test")
        
        methods = ['create_table', 'insert', 'get_by_id', 'get_all', 
                   'filter', 'update', 'delete', 'list_tables', 
                   'drop_table', 'table_exists', 'sort']
        
        for method in methods:
            self.assertTrue(hasattr(db, method), f"Missing method: {method}")


if __name__ == "__main__":
    unittest.main()