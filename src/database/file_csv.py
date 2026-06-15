"""CSV file-based database implementation (bonus task)."""

import json
import csv
import os
from datetime import datetime
from typing import Dict, List, Any

from src.database.interfaces import DatabaseInterface
from src.database.errors import DatabaseError, RecordNotFoundError, ValidationError
from src.database.validators import validate_record


class FileDatabaseCSV(DatabaseInterface):
    """CSV file-based database implementation."""
    
    def __init__(self, directory: str):
        self.directory = directory
        self._tables: Dict[str, List[Dict[str, Any]]] = {}
        self._schemas: Dict[str, Dict[str, type]] = {}
        self._next_ids: Dict[str, int] = {}
        self._load_all()
    
    def _get_table_path(self, table_name: str) -> str:
        return os.path.join(self.directory, f"{table_name}.csv")
    
    def _get_schema_path(self, table_name: str) -> str:
        return os.path.join(self.directory, f"{table_name}_schema.json")
    
    def _load_all(self) -> None:
        """Load all tables from CSV files."""
        os.makedirs(self.directory, exist_ok=True)
        
        for filename in os.listdir(self.directory):
            if filename.endswith(".csv"):
                table_name = filename[:-4]
                self._load_table(table_name)
    
    def _load_table(self, table_name: str) -> None:
        """Load a single table from CSV."""
        csv_path = self._get_table_path(table_name)
        schema_path = self._get_schema_path(table_name)
        
        # Load schema
        if os.path.exists(schema_path):
            try:
                with open(schema_path, 'r', encoding='utf-8') as f:
                    schema_raw = json.load(f)
                    self._schemas[table_name] = {}
                    for field, type_str in schema_raw.items():
                        if type_str == "str":
                            self._schemas[table_name][field] = str
                        elif type_str == "int":
                            self._schemas[table_name][field] = int
                        elif type_str == "float":
                            self._schemas[table_name][field] = float
            except Exception as e:
                raise DatabaseError(f"Ошибка загрузки схемы {table_name}: {e}")
        
        # Load data from CSV
        self._tables[table_name] = []
        max_id = 0
        
        if os.path.exists(csv_path):
            try:
                with open(csv_path, 'r', encoding='utf-8', newline='') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # Convert types based on schema
                        if table_name in self._schemas:
                            for field, field_type in self._schemas[table_name].items():
                                if field in row and row[field]:
                                    try:
                                        if field_type is int:
                                            row[field] = int(row[field])
                                        elif field_type is float:
                                            row[field] = float(row[field])
                                    except (ValueError, TypeError):
                                        pass
                        # Convert id to int
                        if "id" in row:
                            row["id"] = int(row["id"])
                        self._tables[table_name].append(row)
                        if row.get("id", 0) > max_id:
                            max_id = row["id"]
            except Exception as e:
                raise DatabaseError(f"Ошибка загрузки CSV {table_name}: {e}")
        
        self._next_ids[table_name] = max_id + 1
    
    def _save_table(self, table_name: str) -> None:
        """Save table to CSV."""
        csv_path = self._get_table_path(table_name)
        schema_path = self._get_schema_path(table_name)
        
        # Save schema
        if table_name in self._schemas:
            schemas_for_save = {}
            for field, field_type in self._schemas[table_name].items():
                schemas_for_save[field] = field_type.__name__
            with open(schema_path, 'w', encoding='utf-8') as f:
                json.dump(schemas_for_save, f, ensure_ascii=False, indent=2)
        
        # Save data - if table is empty, create file with header only
        if self._tables.get(table_name) and len(self._tables[table_name]) > 0:
            fieldnames = list(self._tables[table_name][0].keys())
            with open(csv_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self._tables[table_name])
        else:
            # Table is empty - create file with header from schema
            if table_name in self._schemas:
                fieldnames = list(self._schemas[table_name].keys())
                if "id" not in fieldnames:
                    fieldnames = ["id", "created_at", "updated_at"] + fieldnames
                with open(csv_path, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
    
    def create_table(self, table_name: str, schema: Dict[str, type]) -> None:
        """Create a new table."""
        if table_name in self._tables:
            raise DatabaseError(f"Таблица '{table_name}' уже существует")
        self._tables[table_name] = []
        self._next_ids[table_name] = 1
        self._schemas[table_name] = schema
        self._save_table(table_name)
    
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
        
        self._tables[table_name].append(record)
        self._next_ids[table_name] += 1
        self._save_table(table_name)
        return record
    
    def get_by_id(self, table_name: str, record_id: int) -> Dict[str, Any]:
        """Get record by ID."""
        if not self.table_exists(table_name):
            raise DatabaseError(f"Таблица '{table_name}' не существует")
        for record in self._tables[table_name]:
            if record["id"] == record_id:
                return record
        raise RecordNotFoundError(f"Запись id={record_id} не найдена")
    
    def get_all(self, table_name: str) -> List[Dict[str, Any]]:
        """Get all records."""
        if not self.table_exists(table_name):
            raise DatabaseError(f"Таблица '{table_name}' не существует")
        return self._tables[table_name]
    
    def filter(self, table_name: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter records."""
        if not self.table_exists(table_name):
            raise DatabaseError(f"Таблица '{table_name}' не существует")
        
        results = self._tables[table_name].copy()
        
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
        
        schema = self._schemas[table_name]
        
        # Check that all updated fields exist in schema
        for field in updates:
            if field not in schema:
                raise ValidationError(
                    f"Поле '{field}' не существует в схеме таблицы '{table_name}'. "
                    f"Допустимые поля: {', '.join(schema.keys())}"
                )
        
        for i, record in enumerate(self._tables[table_name]):
            if record["id"] == record_id:
                for field, value in updates.items():
                    if field in schema:
                        if not isinstance(value, schema[field]):
                            raise ValidationError(
                                f"Поле '{field}' должно быть {schema[field].__name__}, "
                                f"получен {type(value).__name__}"
                            )
                
                self._tables[table_name][i].update(updates)
                self._tables[table_name][i]["updated_at"] = datetime.now().isoformat()
                self._save_table(table_name)
                return self._tables[table_name][i]
        
        raise RecordNotFoundError(f"Запись id={record_id} не найдена")
    
    def delete(self, table_name: str, record_id: int) -> None:
        """Delete a record."""
        if not self.table_exists(table_name):
            raise DatabaseError(f"Таблица '{table_name}' не существует")
        
        for i, record in enumerate(self._tables[table_name]):
            if record["id"] == record_id:
                del self._tables[table_name][i]
                self._save_table(table_name)
                return
        
        raise RecordNotFoundError(f"Запись id={record_id} не найдена")
    
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
        
        csv_path = self._get_table_path(table_name)
        schema_path = self._get_schema_path(table_name)
        if os.path.exists(csv_path):
            os.remove(csv_path)
        if os.path.exists(schema_path):
            os.remove(schema_path)
    
    def table_exists(self, table_name: str) -> bool:
        """Check if table exists."""
        return table_name in self._tables
    
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
            if field in self._schemas.get(table_name, {}):
                if self._schemas[table_name][field] in (int, float):
                    try:
                        value = int(value) if value else 0
                    except (ValueError, TypeError):
                        value = 0
            return (0, value)
        
        results.sort(key=get_sort_key, reverse=reverse)
        return results