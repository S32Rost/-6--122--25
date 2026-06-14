"""Tests for custom exceptions."""

import unittest
from src.database.errors import DatabaseError, RecordNotFoundError, ValidationError


class TestErrors(unittest.TestCase):
    """Test exception hierarchy."""
    
    def test_database_error(self):
        error = DatabaseError("Ошибка БД")
        self.assertEqual(str(error), "Ошибка БД")
        self.assertIsInstance(error, Exception)
    
    def test_record_not_found_error(self):
        error = RecordNotFoundError("Запись не найдена")
        self.assertEqual(str(error), "Запись не найдена")
        self.assertIsInstance(error, DatabaseError)
    
    def test_validation_error(self):
        error = ValidationError("Ошибка валидации")
        self.assertEqual(str(error), "Ошибка валидации")
        self.assertIsInstance(error, DatabaseError)
    
    def test_error_hierarchy(self):
        self.assertTrue(issubclass(RecordNotFoundError, DatabaseError))
        self.assertTrue(issubclass(ValidationError, DatabaseError))
        self.assertTrue(issubclass(DatabaseError, Exception))


if __name__ == "__main__":
    unittest.main()