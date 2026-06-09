class DatabaseError(Exception):
    """Базовое исключение для БД."""
    pass

class RecordNotFoundError(DatabaseError):
    """Запись не найдена."""
    pass

class ValidationError(DatabaseError):
    """Ошибка валидации данных."""
    pass