"""Validation functions."""

from src.database.errors import ValidationError


def validate_student_data(name: str, age: int, major: str) -> None:
    """Validate student data fields."""
    if not name or not isinstance(name, str) or len(name.strip()) == 0:
        raise ValidationError("Имя не может быть пустым")
    
    if not isinstance(age, int) or age < 16 or age > 120:
        raise ValidationError("Возраст должен быть от 16 до 120 лет")
    
    if not major or not isinstance(major, str) or len(major.strip()) == 0:
        raise ValidationError("Специальность не может быть пустой")


def validate_record(schema: dict, data: dict) -> None:
    """Validate record against schema."""
    for field, field_type in schema.items():
        if field not in data:
            raise ValidationError(f"Отсутствует поле: {field}")
        if not isinstance(data[field], field_type):
            raise ValidationError(
                f"Поле '{field}' должно быть {field_type.__name__}"
            )