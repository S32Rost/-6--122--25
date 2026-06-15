"""In-memory database implementation."""

from datetime import datetime
from typing import Dict, List, Any

from src.database.interfaces import DatabaseInterface
from src.database.errors import DatabaseError, RecordNotFoundError, ValidationError
from src.database.validators import validate_record


class InMemoryDatabase(DatabaseInterface):
    """In-memory database implementation."""
    
    def __init__(self, name: str = "main_db"):
        self.name = name
        self._tables: Dict[str, Dict] = {}
        self._next_ids: Dict[str, int] = {}
        self._schemas: Dict[str, Dict[str, type]] = {}
    
    def create_table(self, table_name: str, schema: Dict[str, type]) -> None:
        """Create a new table."""
        if table_name in self._tables:
            raise DatabaseError(f"Таблица '{table_name}' уже существует")
        self._tables[table_name] = {}
        self._next_ids[table_name] = 1
        self._schemas[table_name] = schema
    
    def insert(self, table_name: str, **kwargs) -> Dict[str, Any]:
        """Insert a new record."""
        if not self.table_exists(table_name):
            raise DatabaseError(f"Таблица '{table_name}' не существует")
        
        validate_record(self._schemas[table_name], kwargs)
        
        record_id = self._next_ids[table_name]
        record = {
            "id": record_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            **kwargs
        }
        
        self._tables[table_name][record_id] = record
        self._next_ids[table_name] += 1
        return record
    
    def get_by_id(self, table_name: str, record_id: int) -> Dict[str, Any]:
        """Get record by ID."""
        if not self.table_exists(table_name):
            raise DatabaseError(f"Таблица '{table_name}' не существует")
        if record_id not in self._tables[table_name]:
            raise RecordNotFoundError(f"Запись id={record_id} не найдена")
        return self._tables[table_name][record_id]
    
    def get_all(self, table_name: str) -> List[Dict[str, Any]]:
        """Get all records."""
        if not self.table_exists(table_name):
            raise DatabaseError(f"Таблица '{table_name}' не существует")
        return list(self._tables[table_name].values())
    
    def filter(self, table_name: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter records."""
        if not self.table_exists(table_name):
            raise DatabaseError(f"Таблица '{table_name}' не существует")
        
        results = list(self._tables[table_name].values())
        
        for filter_key, filter_value in filters.items():
            if "__" in filter_key:
                field, operator = filter_key.split("__", 1)
            else:
                field, operator = filter_key, "eq"
            
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
    
    def update(self, table_name: str, record_id: int, **updates) -> Dict[str, Any]:
        """Update a record."""
        if not self.table_exists(table_name):
            raise DatabaseError(f"Таблица '{table_name}' не существует")
        if record_id not in self._tables[table_name]:
            raise RecordNotFoundError(f"Запись id={record_id} не найдена")
        
        schema = self._schemas[table_name]
        
        # Проверяем, что все обновляемые поля есть в схеме
        for field in updates:
            if field not in schema:
                raise ValidationError(
                    f"Поле '{field}' не существует в схеме таблицы '{table_name}'. "
                    f"Допустимые поля: {', '.join(schema.keys())}"
                )
        
        # Проверяем типы обновляемых полей
        for field, value in updates.items():
            if field in schema:
                if not isinstance(value, schema[field]):
                    raise ValidationError(
                        f"Поле '{field}' должно быть {schema[field].__name__}, "
                        f"получен {type(value).__name__}"
                    )
        
        self._tables[table_name][record_id].update(updates)
        self._tables[table_name][record_id]["updated_at"] = datetime.now().isoformat()
        return self._tables[table_name][record_id]
    
    def delete(self, table_name: str, record_id: int) -> None:
        """Delete a record."""
        if not self.table_exists(table_name):
            raise DatabaseError(f"Таблица '{table_name}' не существует")
        if record_id not in self._tables[table_name]:
            raise RecordNotFoundError(f"Запись id={record_id} не найдена")
        del self._tables[table_name][record_id]
    
    def list_tables(self) -> List[str]:
        """List all tables."""
        return list(self._tables.keys())
    
    def drop_table(self, table_name: str) -> None:
        """Drop a table."""
        if not self.table_exists(table_name):
            raise DatabaseError(f"Таблица '{table_name}' не существует")
        del self._tables[table_name]
        del self._next_ids[table_name]
        del self._schemas[table_name]
    
    def table_exists(self, table_name: str) -> bool:
        """Check if table exists."""
        return table_name in self._tables
    
    def sort(self, table_name: str, field: str, reverse: bool = False) -> List[Dict[str, Any]]:
        """Sort records by field."""
        if not self.table_exists(table_name):
            raise DatabaseError(f"Таблица '{table_name}' не существует")
        
        # Проверяем, существует ли поле для сортировки
        if field not in self._schemas.get(table_name, {}) and field != "id":
            raise ValidationError(f"Поле '{field}' не существует для сортировки")
        
        results = self.get_all(table_name)
        
        def get_sort_key(record):
            value = record.get(field)
            if value is None:
                return (1, None)
            if isinstance(value, str):
                return (0, value.lower())
            return (0, value)
        
        results.sort(key=get_sort_key, reverse=reverse)
        return results