"""Pytest fixtures for database tests."""

import pytest
import tempfile
import os
import shutil

from src.database.in_memory import InMemoryDatabase
from src.database.file_json import FileDatabaseJSON
from src.database.file_csv import FileDatabaseCSV
from src.database.schemas import SCHEMAS


@pytest.fixture
def in_memory_db():
    """Create in-memory database instance."""
    db = InMemoryDatabase("test_db")
    db.create_table("students", SCHEMAS["students"])
    return db


@pytest.fixture
def json_db():
    """Create JSON database instance with temp file."""
    temp_file = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
    temp_file.close()
    db = FileDatabaseJSON(temp_file.name)
    db.create_table("students", SCHEMAS["students"])
    yield db
    if os.path.exists(temp_file.name):
        os.remove(temp_file.name)


@pytest.fixture
def csv_db():
    """Create CSV database instance with temp directory."""
    temp_dir = tempfile.mkdtemp()
    db = FileDatabaseCSV(temp_dir)
    db.create_table("students", SCHEMAS["students"])
    yield db
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_students(in_memory_db):
    """Insert sample student records."""
    students = [
        {"name": "Иван Петров", "age": 20, "major": "Информатика", "email": "ivan@test.com"},
        {"name": "Мария Сидорова", "age": 19, "major": "Математика", "email": "maria@test.com"},
        {"name": "Алексей Иванов", "age": 22, "major": "Физика", "email": "alex@test.com"},
        {"name": "Анна Козлова", "age": 21, "major": "Информатика", "email": "anna@test.com"},
    ]
    for student in students:
        in_memory_db.insert("students", **student)
    return in_memory_db