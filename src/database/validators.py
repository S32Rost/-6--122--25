"""Validation functions for all data types."""

import re
from datetime import datetime
from typing import Any, Dict, Type

from src.database.errors import ValidationError


def validate_student_data(name: str, age: int, major: str, email: str = None) -> None:
    """Validate student data fields."""
    # Проверка имени
    if not name or not isinstance(name, str) or len(name.strip()) == 0:
        raise ValidationError("Имя не может быть пустым")
    
    if len(name) > 100:
        raise ValidationError("Имя не может быть длиннее 100 символов")
    
    if not re.match(r'^[а-яА-Яa-zA-Z\s\-]+$', name):
        raise ValidationError("Имя может содержать только буквы, пробелы и дефисы")
    
    # Проверка возраста
    if not isinstance(age, int):
        raise ValidationError("Возраст должен быть целым числом")
    
    if age < 16 or age > 120:
        raise ValidationError("Возраст должен быть от 16 до 120 лет")
    
    # Проверка специальности
    if not major or not isinstance(major, str) or len(major.strip()) == 0:
        raise ValidationError("Специальность не может быть пустой")
    
    if len(major) > 100:
        raise ValidationError("Специальность не может быть длиннее 100 символов")
    
    # Проверка email (если передан)
    if email is not None:
        if not isinstance(email, str):
            raise ValidationError("Email должен быть строкой")
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValidationError("Неверный формат email")


def validate_book_data(title: str, author: str, year: int, isbn: str = None) -> None:
    """Validate book data fields."""
    # Название
    if not title or not isinstance(title, str) or len(title.strip()) == 0:
        raise ValidationError("Название книги не может быть пустым")
    
    if len(title) > 200:
        raise ValidationError("Название не может быть длиннее 200 символов")
    
    # Автор
    if not author or not isinstance(author, str) or len(author.strip()) == 0:
        raise ValidationError("Автор не может быть пустым")
    
    if len(author) > 100:
        raise ValidationError("Автор не может быть длиннее 100 символов")
    
    # Год
    if not isinstance(year, int):
        raise ValidationError("Год должен быть целым числом")
    
    current_year = datetime.now().year
    if year < 1450 or year > current_year + 5:
        raise ValidationError(f"Год должен быть между 1450 и {current_year + 5}")
    
    # ISBN (если передан)
    if isbn is not None:
        if not isinstance(isbn, str):
            raise ValidationError("ISBN должен быть строкой")
        
        isbn_clean = isbn.replace('-', '').replace(' ', '')
        if len(isbn_clean) not in [10, 13]:
            raise ValidationError("ISBN должен содержать 10 или 13 цифр")
        
        if not isbn_clean.isdigit():
            raise ValidationError("ISBN должен содержать только цифры и дефисы")


def validate_employee_data(full_name: str, position: str, salary: float, department: str) -> None:
    """Validate employee data fields."""
    # ФИО
    if not full_name or not isinstance(full_name, str) or len(full_name.strip()) == 0:
        raise ValidationError("ФИО сотрудника не может быть пустым")
    
    if len(full_name) > 150:
        raise ValidationError("ФИО не может быть длиннее 150 символов")
    
    # Должность
    if not position or not isinstance(position, str) or len(position.strip()) == 0:
        raise ValidationError("Должность не может быть пустой")
    
    if len(position) > 100:
        raise ValidationError("Должность не может быть длиннее 100 символов")
    
    # Зарплата
    if not isinstance(salary, (int, float)):
        raise ValidationError("Зарплата должна быть числом")
    
    if salary < 0:
        raise ValidationError("Зарплата не может быть отрицательной")
    
    if salary > 1_000_000:
        raise ValidationError("Зарплата не может превышать 1 000 000")
    
    # Отдел
    if not department or not isinstance(department, str) or len(department.strip()) == 0:
        raise ValidationError("Отдел не может быть пустым")


def validate_record(schema: Dict[str, Type], data: Dict[str, Any]) -> None:
    """Validate record against schema with full validation."""
    # Проверка наличия всех полей
    for field, field_type in schema.items():
        if field not in data:
            raise ValidationError(f"Отсутствует поле: {field}")
        
        # Проверка типа
        if not isinstance(data[field], field_type):
            raise ValidationError(
                f"Поле '{field}' должно быть {field_type.__name__}, "
                f"получен {type(data[field]).__name__}"
            )
    
    # Дополнительная валидация в зависимости от схемы
    if "name" in schema and "age" in schema and "major" in schema:
        # Схема students
        validate_student_data(
            name=data.get("name"),
            age=data.get("age"),
            major=data.get("major"),
            email=data.get("email")
        )
    elif "title" in schema and "author" in schema and "year" in schema:
        # Схема books
        validate_book_data(
            title=data.get("title"),
            author=data.get("author"),
            year=data.get("year"),
            isbn=data.get("isbn")
        )
    elif "full_name" in schema and "position" in schema and "salary" in schema:
        # Схема employees
        validate_employee_data(
            full_name=data.get("full_name"),
            position=data.get("position"),
            salary=data.get("salary"),
            department=data.get("department")
        )