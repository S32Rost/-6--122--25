"""Tests for validators."""

import unittest
from src.database.validators import validate_student_data, validate_record
from src.database.errors import ValidationError


class TestValidators(unittest.TestCase):
    """Test validation functions."""
    
    def test_valid_student_data(self):
        try:
            validate_student_data("Иван", 20, "Информатика")
        except ValidationError:
            self.fail("ValidationError raised unexpectedly")
    
    def test_empty_name(self):
        with self.assertRaises(ValidationError):
            validate_student_data("", 20, "Информатика")
    
    def test_whitespace_name(self):
        with self.assertRaises(ValidationError):
            validate_student_data("   ", 20, "Информатика")
    
    def test_none_name(self):
        with self.assertRaises(ValidationError):
            validate_student_data(None, 20, "Информатика")
    
    def test_age_too_low(self):
        with self.assertRaises(ValidationError):
            validate_student_data("Иван", 15, "Информатика")
    
    def test_age_too_high(self):
        with self.assertRaises(ValidationError):
            validate_student_data("Иван", 121, "Информатика")
    
    def test_negative_age(self):
        with self.assertRaises(ValidationError):
            validate_student_data("Иван", -5, "Информатика")
    
    def test_empty_major(self):
        with self.assertRaises(ValidationError):
            validate_student_data("Иван", 20, "")
    
    def test_whitespace_major(self):
        with self.assertRaises(ValidationError):
            validate_student_data("Иван", 20, "   ")
    
    def test_validate_record_success(self):
        schema = {"name": str, "age": int}
        data = {"name": "Иван", "age": 20}
        try:
            validate_record(schema, data)
        except ValidationError:
            self.fail("ValidationError raised unexpectedly")
    
    def test_validate_record_missing_field(self):
        schema = {"name": str, "age": int}
        data = {"name": "Иван"}
        with self.assertRaises(ValidationError):
            validate_record(schema, data)
    
    def test_validate_record_wrong_type(self):
        schema = {"name": str, "age": int}
        data = {"name": "Иван", "age": "twenty"}
        with self.assertRaises(ValidationError):
            validate_record(schema, data)


if __name__ == "__main__":
    unittest.main()