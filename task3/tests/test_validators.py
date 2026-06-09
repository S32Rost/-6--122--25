import unittest
from validators import validate_student_data
from errors import ValidationError

class TestValidators(unittest.TestCase):
    def test_valid_data(self):
        try:
            validate_student_data("Иван", 20, "Информатика")
        except ValidationError:
            self.fail("Валидация не должна была выбросить исключение")
    
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
    
    def test_age_zero(self):
        with self.assertRaises(ValidationError):
            validate_student_data("Иван", 0, "Информатика")
    
    def test_negative_age(self):
        with self.assertRaises(ValidationError):
            validate_student_data("Иван", -5, "Информатика")
    
    def test_empty_major(self):
        with self.assertRaises(ValidationError):
            validate_student_data("Иван", 20, "")
    
    def test_whitespace_major(self):
        with self.assertRaises(ValidationError):
            validate_student_data("Иван", 20, "   ")
    
    def test_none_major(self):
        with self.assertRaises(ValidationError):
            validate_student_data("Иван", 20, None)


if __name__ == "__main__":
    unittest.main()