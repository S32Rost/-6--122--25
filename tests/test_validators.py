"""Tests for validators - расширенные тесты."""

import unittest
from src.database.validators import (
    validate_student_data,
    validate_book_data,
    validate_employee_data,
    validate_record
)
from src.database.errors import ValidationError
from src.database.schemas import SCHEMAS


class TestValidatorsExtended(unittest.TestCase):
    """Extended validation tests for coverage."""
    
    # Тесты для validate_student_data
    def test_name_too_long(self):
        with self.assertRaises(ValidationError):
            validate_student_data("A" * 101, 20, "Информатика", "test@test.com")
    
    def test_name_invalid_chars(self):
        with self.assertRaises(ValidationError):
            validate_student_data("Иван123", 20, "Информатика", "test@test.com")
    
    def test_age_string(self):
        with self.assertRaises(ValidationError):
            validate_student_data("Иван", "двадцать", "Информатика", "test@test.com")
    
    def test_major_too_long(self):
        with self.assertRaises(ValidationError):
            validate_student_data("Иван", 20, "A" * 101, "test@test.com")
    
    def test_invalid_email(self):
        with self.assertRaises(ValidationError):
            validate_student_data("Иван", 20, "Информатика", "invalid-email")
    
    def test_email_not_string(self):
        with self.assertRaises(ValidationError):
            validate_student_data("Иван", 20, "Информатика", 123)
    
    # Тесты для validate_book_data
    def test_empty_title(self):
        with self.assertRaises(ValidationError):
            validate_book_data("", "Автор", 2020, "1234567890")
    
    def test_title_too_long(self):
        with self.assertRaises(ValidationError):
            validate_book_data("A" * 201, "Автор", 2020, "1234567890")
    
    def test_empty_author(self):
        with self.assertRaises(ValidationError):
            validate_book_data("Книга", "", 2020, "1234567890")
    
    def test_author_too_long(self):
        with self.assertRaises(ValidationError):
            validate_book_data("Книга", "A" * 101, 2020, "1234567890")
    
    def test_year_too_early(self):
        with self.assertRaises(ValidationError):
            validate_book_data("Книга", "Автор", 1400, "1234567890")
    
    def test_invalid_isbn_length(self):
        with self.assertRaises(ValidationError):
            validate_book_data("Книга", "Автор", 2020, "123")
    
    def test_invalid_isbn_chars(self):
        with self.assertRaises(ValidationError):
            validate_book_data("Книга", "Автор", 2020, "abc")
    
    # Тесты для validate_employee_data
    def test_empty_full_name(self):
        with self.assertRaises(ValidationError):
            validate_employee_data("", "Программист", 50000, "IT")
    
    def test_full_name_too_long(self):
        with self.assertRaises(ValidationError):
            validate_employee_data("A" * 151, "Программист", 50000, "IT")
    
    def test_empty_position(self):
        with self.assertRaises(ValidationError):
            validate_employee_data("Иван Иванов", "", 50000, "IT")
    
    def test_position_too_long(self):
        with self.assertRaises(ValidationError):
            validate_employee_data("Иван Иванов", "A" * 101, 50000, "IT")
    
    def test_negative_salary(self):
        with self.assertRaises(ValidationError):
            validate_employee_data("Иван Иванов", "Программист", -1000, "IT")
    
    def test_salary_too_high(self):
        with self.assertRaises(ValidationError):
            validate_employee_data("Иван Иванов", "Программист", 2_000_000, "IT")
    
    def test_salary_wrong_type(self):
        with self.assertRaises(ValidationError):
            validate_employee_data("Иван Иванов", "Программист", "много", "IT")
    
    def test_empty_department(self):
        with self.assertRaises(ValidationError):
            validate_employee_data("Иван Иванов", "Программист", 50000, "")
    
    # Тесты для validate_record со всеми схемами
    def test_validate_record_students_success(self):
        schema = SCHEMAS["students"]
        data = {"name": "Иван", "age": 20, "major": "Информатика", "email": "ivan@test.com"}
        try:
            validate_record(schema, data)
        except ValidationError:
            self.fail("ValidationError raised unexpectedly")
    
    def test_validate_record_books_success(self):
        schema = SCHEMAS["books"]
        data = {"title": "Война и мир", "author": "Толстой", "year": 1869, "isbn": "978-5-17-113922-7"}
        try:
            validate_record(schema, data)
        except ValidationError:
            self.fail("ValidationError raised unexpectedly")
    
    def test_validate_record_employees_success(self):
        schema = SCHEMAS["employees"]
        data = {"full_name": "Иван Иванов", "position": "Программист", "salary": 100000.0, "department": "IT"}
        try:
            validate_record(schema, data)
        except ValidationError:
            self.fail("ValidationError raised unexpectedly")


if __name__ == "__main__":
    unittest.main()
