from typing import Dict, List, Any, Optional
from datetime import datetime
from models import Student
from errors import RecordNotFoundError, ValidationError, DatabaseError
from validators import validate_student_data

class Table:
    """Общий класс для любой таблицы в базе данных."""
    
    def __init__(self, name: str, schema: Dict[str, type]):
        """
        name: имя таблицы
        schema: схема таблицы {имя_поля: тип}
        """
        self.name = name
        self.schema = schema
        self._records: Dict[int, Dict[str, Any]] = {}
        self._next_id = 1
    
    def insert(self, **kwargs) -> Dict[str, Any]:
        """Добавление новой записи."""
        # Проверяем, что все обязательные поля заполнены
        for field in self.schema:
            if field not in kwargs and field != "id":
                raise ValidationError(f"Отсутствует обязательное поле: {field}")
        
        # Валидируем типы
        for field, value in kwargs.items():
            if field in self.schema:
                expected_type = self.schema[field]
                if not isinstance(value, expected_type):
                    raise ValidationError(
                        f"Поле '{field}' должно быть типа {expected_type.__name__}, "
                        f"получен {type(value).__name__}"
                    )
        
        # Добавляем служебные поля
        record = {
            "id": self._next_id,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            **kwargs
        }
        
        self._records[self._next_id] = record
        self._next_id += 1
        return record
    
    def get_by_id(self, record_id: int) -> Dict[str, Any]:
        """Получение записи по ID."""
        if record_id not in self._records:
            raise RecordNotFoundError(f"Запись с id={record_id} не найдена в таблице '{self.name}'")
        return self._records[record_id]
    
    def filter(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Фильтрация записей с поддержкой разных операторов.
        Формат: {"field__operator": value}
        Операторы: eq, gt, lt, contains, startswith
        """
        results = list(self._records.values())
        
        for filter_key, filter_value in filters.items():
            if filter_value is None:
                continue
            
            # Разбираем оператор
            if "__" in filter_key:
                field, operator = filter_key.split("__", 1)
            else:
                field, operator = filter_key, "eq"
            
            if field not in self.schema and field != "id":
                raise ValidationError(f"Неподдерживаемое поле для фильтрации: {field}")
            
            if operator == "eq":
                results = [r for r in results if r.get(field) == filter_value]
            elif operator == "gt":
                results = [r for r in results if r.get(field, 0) > filter_value]
            elif operator == "lt":
                results = [r for r in results if r.get(field, 0) < filter_value]
            elif operator == "contains":
                results = [r for r in results if filter_value.lower() in str(r.get(field, "")).lower()]
            elif operator == "startswith":
                results = [r for r in results if str(r.get(field, "")).lower().startswith(filter_value.lower())]
            else:
                raise ValidationError(f"Неподдерживаемый оператор: {operator}")
        
        return results
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Получить все записи."""
        return list(self._records.values())
    
    def update(self, record_id: int, **updates) -> Dict[str, Any]:
        """Обновление записи."""
        if record_id not in self._records:
            raise RecordNotFoundError(f"Запись с id={record_id} не найдена в таблице '{self.name}'")
        
        # Валидируем типы для обновляемых полей
        for field, value in updates.items():
            if field in self.schema:
                expected_type = self.schema[field]
                if not isinstance(value, expected_type):
                    raise ValidationError(
                        f"Поле '{field}' должно быть типа {expected_type.__name__}, "
                        f"получен {type(value).__name__}"
                    )
        
        self._records[record_id].update(updates)
        self._records[record_id]["updated_at"] = datetime.now()
        return self._records[record_id]
    
    def delete(self, record_id: int) -> None:
        """Удаление записи."""
        if record_id not in self._records:
            raise RecordNotFoundError(f"Запись с id={record_id} не найдена в таблице '{self.name}'")
        del self._records[record_id]
    
    def count(self) -> int:
        """Количество записей в таблице."""
        return len(self._records)
    
    def clear(self) -> None:
        """Очистить все записи в таблице."""
        self._records.clear()
        self._next_id = 1


class Database:
    """Класс базы данных, управляющий несколькими таблицами."""
    
    def __init__(self, name: str = "main_db"):
        self.name = name
        self._tables: Dict[str, Table] = {}
    
    def create_table(self, name: str, schema: Dict[str, type]) -> Table:
        """Создать новую таблицу."""
        if name in self._tables:
            raise DatabaseError(f"Таблица '{name}' уже существует")
        
        table = Table(name, schema)
        self._tables[name] = table
        return table
    
    def get_table(self, name: str) -> Table:
        """Получить таблицу по имени."""
        if name not in self._tables:
            raise DatabaseError(f"Таблица '{name}' не существует")
        return self._tables[name]
    
    def list_tables(self) -> List[str]:
        """Список всех таблиц в базе."""
        return list(self._tables.keys())
    
    def drop_table(self, name: str) -> None:
        """Удалить таблицу."""
        if name not in self._tables:
            raise DatabaseError(f"Таблица '{name}' не существует")
        del self._tables[name]
    
    def table_exists(self, name: str) -> bool:
        """Проверить существование таблицы."""
        return name in self._tables


# Создание готовых схем для популярных таблиц
SCHEMAS = {
    "students": {
        "name": str,
        "age": int,
        "major": str,
        "email": str
    },
    "books": {
        "title": str,
        "author": str,
        "year": int,
        "isbn": str
    },
    "employees": {
        "full_name": str,
        "position": str,
        "salary": float,
        "department": str
    }
}