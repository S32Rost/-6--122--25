from typing import Dict, List, Any, Optional
from datetime import datetime
from errors import RecordNotFoundError, ValidationError, DatabaseError

class Table:
    """Класс для работы с таблицей в БД."""
    
    def __init__(self, name: str, schema: Dict[str, type]):
        self.name = name
        self.schema = schema
        self._records: Dict[int, Dict[str, Any]] = {}
        self._next_id = 1
    
    def insert(self, **kwargs) -> Dict[str, Any]:
        """Добавление записи."""
        for field in self.schema:
            if field not in kwargs:
                raise ValidationError(f"Отсутствует поле: {field}")
        
        for field, value in kwargs.items():
            if field in self.schema:
                expected_type = self.schema[field]
                if not isinstance(value, expected_type):
                    raise ValidationError(
                        f"Поле '{field}' должно быть {expected_type.__name__}"
                    )
        
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
        if record_id not in self._records:
            raise RecordNotFoundError(f"Запись id={record_id} не найдена")
        return self._records[record_id]
    
    def filter(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        results = list(self._records.values())
        
        for filter_key, filter_value in filters.items():
            if "__" in filter_key:
                field, operator = filter_key.split("__", 1)
            else:
                field, operator = filter_key, "eq"
            
            if field not in self.schema and field != "id":
                raise ValidationError(f"Поле '{field}' не существует")
            
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
                raise ValidationError(f"Оператор '{operator}' не поддерживается")
        
        return results
    
    def sort(self, field: str, reverse: bool = False) -> List[Dict[str, Any]]:
        """
        Сортировка записей по указанному полю.
        
        Args:
            field: Имя поля для сортировки
            reverse: False - по возрастанию, True - по убыванию
        
        Returns:
            Отсортированный список записей
        """
        if field not in self.schema and field != "id":
            raise ValidationError(f"Поле '{field}' не существует для сортировки")
        
        results = list(self._records.values())
        
        # Обрабатываем возможные типы данных
        def get_sort_key(record):
            value = record.get(field)
            # None значения отправляем в конец
            if value is None:
                return (1, None) if not reverse else (1, None)
            # Для строк - приводим к нижнему регистру для case-insensitive сортировки
            if isinstance(value, str):
                return (0, value.lower())
            return (0, value)
        
        results.sort(key=get_sort_key, reverse=reverse)
        return results
    
    def get_all_sorted(self, field: str = "id", reverse: bool = False) -> List[Dict[str, Any]]:
        """Получить все записи, отсортированные по указанному полю."""
        return self.sort(field, reverse)
    
    def get_all(self) -> List[Dict[str, Any]]:
        return list(self._records.values())
    
    def update(self, record_id: int, **updates) -> Dict[str, Any]:
        if record_id not in self._records:
            raise RecordNotFoundError(f"Запись id={record_id} не найдена")
        
        for field, value in updates.items():
            if field in self.schema:
                expected_type = self.schema[field]
                if not isinstance(value, expected_type):
                    raise ValidationError(
                        f"Поле '{field}' должно быть {expected_type.__name__}"
                    )
        
        self._records[record_id].update(updates)
        self._records[record_id]["updated_at"] = datetime.now()
        return self._records[record_id]
    
    def delete(self, record_id: int) -> None:
        if record_id not in self._records:
            raise RecordNotFoundError(f"Запись id={record_id} не найдена")
        del self._records[record_id]
    
    def count(self) -> int:
        return len(self._records)
    
    def clear(self) -> None:
        self._records.clear()
        self._next_id = 1


class Database:
    """Управление несколькими таблицами."""
    
    def __init__(self, name: str = "main_db"):
        self.name = name
        self._tables: Dict[str, Table] = {}
    
    def create_table(self, name: str, schema: Dict[str, type]) -> Table:
        if name in self._tables:
            raise DatabaseError(f"Таблица '{name}' уже существует")
        
        table = Table(name, schema)
        self._tables[name] = table
        return table
    
    def get_table(self, name: str) -> Table:
        if name not in self._tables:
            raise DatabaseError(f"Таблица '{name}' не существует")
        return self._tables[name]
    
    def list_tables(self) -> List[str]:
        return list(self._tables.keys())
    
    def drop_table(self, name: str) -> None:
        if name not in self._tables:
            raise DatabaseError(f"Таблица '{name}' не существует")
        del self._tables[name]
    
    def table_exists(self, name: str) -> bool:
        return name in self._tables


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