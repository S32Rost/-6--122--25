"""JSON file-based database implementation."""

import json
import os
from datetime import datetime
from typing import Dict, List, Any

from src.database.interfaces import DatabaseInterface
from src.database.errors import DatabaseError, RecordNotFoundError, ValidationError
from src.database.validators import validate_record


class FileDatabaseJSON(DatabaseInterface):
    """JSON file-based database implementation."""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self._data: Dict[str, Dict] = {}
        self._schemas: Dict[str, Dict[str, type]] = {}
        self._next_ids: Dict[str, int] = {}
        self._load()
    
    def _load(self) -> None:
        """Load data from JSON file."""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if not content.strip():
                        self._data = {}
                        self._next_ids = {}
                        self._schemas = {}
                        return
                    loaded = json.loads(content)
                    self._data = loaded.get("tables", {})
                    self._next_ids = loaded.get("next_ids", {})
                    schemas_raw = loaded.get("schemas", {})
                    for table_name, schema_raw in schemas_raw.items():
                        self._schemas[table_name] = {}
                        for field, type_str in schema_raw.items():
                            if type_str == "str":
                                self._schemas[table_name][field] = str
                            elif type_str == "int":
                                self._schemas[table_name][field] = int
                            elif type_str == "float":
                                self._schemas[table_name][field] = float
            except json.JSONDecodeError as e:
                raise DatabaseError(f"Ошибка парсинга JSON файла {self.filepath}: файл повреждён. {e}")
            except Exception as e:
                raise DatabaseError(f"Ошибка загрузки файла {self.filepath}: {e}")
    
    def _save(self) -> None:
        """Save data to JSON file."""
        try:
            schemas_for_save = {}
            for table_name, schema in self._schemas.items():
                schemas_for_save[table_name] = {}
                for field, field_type in schema.items():
                    schemas_for_save[table_name][field] = field_type.__name__
            
            data_to_save = {
                "tables": self._data,
                "next_ids": self._next_ids,
                "schemas": schemas_for_save
            }
            
            os.makedirs(os.path.dirname(self.filepath) or ".", exist_ok=True)
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise DatabaseError(f"Ошибка сохранения в файл {self.filepath}: {e}")
    
    def create_table(self, table_name: str, schema: Dict[str, type]) -> None:
        """Create a new table."""
        if table_name in self._data:
            raise DatabaseError(f"Таблица '{table_name}' уже существует")
        self._data[table_name] = {}
        self._next_ids[table_name] = 1
        self._schemas[table_name] = schema
        self._save()
    
    def insert(self, table_name: str, **kwargs) -> Dict[str, Any]:
        """Insert a new record."""
        if not self.table_exists(table_name):
            raise DatabaseError(f"Таблица '{table_name}' не существует")
        
        schema = self._schemas.get(table_name, {})
        validate_record(schema, kwargs)
        
        record_id = self._next_ids[table_name]
        record = {
            "id": record_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            **kwargs
        }
        
        self._data[table_name][str(record_id)] = record
        self._next_ids[table_name] += 1
        self._save()
        return record
    
    def get_by_id(self, table_name: str, record_id: int) -> Dict[str, Any]:
        """Get record by ID."""
        if not self.table_exists(table_name):
            raise DatabaseError(f"Таблица '{table_name}' не существует")
        if str(record_id) not in self._data[table_name]:
            raise RecordNotFoundError(f"Запись id={record_id} не найдена")
        return self._data[table_name][str(record_id)]
    
    def get_all(self, table_name: str) -> List[Dict[str, Any]]:
        """Get all records."""
        if not self.table_exists(table_name):
            raise DatabaseError(f"Таблица '{table_name}' не существует")
        return list(self._data[table_name].values())
    
    def filter(self, table_name: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter records."""
        if not self.table_exists(table_name):
            raise DatabaseError(f"Таблица '{table_name}' не существует")
        
        results = list(self._data[table_name].values())
        
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
        if str(record_id) not in self._data[table_name]:
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
        
        self._data[table_name][str(record_id)].update(updates)
        self._data[table_name][str(record_id)]["updated_at"] = datetime.now().isoformat()
        self._save()
        return self._data[table_name][str(record_id)]
    
    def delete(self, table_name: str, record_id: int) -> None:
        """Delete a record."""
        if not self.table_exists(table_name):
            raise DatabaseError(f"Таблица '{table_name}' не существует")
        if str(record_id) not in self._data[table_name]:
            raise RecordNotFoundError(f"Запись id={record_id} не найдена")
        del self._data[table_name][str(record_id)]
        self._save()
    
    def list_tables(self) -> List[str]:
        """List all tables."""
        return list(self._data.keys())
    
    def drop_table(self, table_name: str) -> None:
        """Drop a table."""
        if not self.table_exists(table_name):
            raise DatabaseError(f"Таблица '{table_name}' не существует")
        del self._data[table_name]
        del self._next_ids[table_name]
        del self._schemas[table_name]
        self._save()
    
    def table_exists(self, table_name: str) -> bool:
        """Check if table exists."""
        return table_name in self._data
    
    def sort(self, table_name: str, field: str, reverse: bool = False) -> List[Dict[str, Any]]:
        """Sort records by field."""
        if not self.table_exists(table_name):
            raise DatabaseError(f"Таблица '{table_name}' не существует")
        
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