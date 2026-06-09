import json
import csv
import os
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime
from errors import RecordNotFoundError, ValidationError, DatabaseError


class DatabaseInterface(ABC):
    """Абстрактный интерфейс для всех БД (in-memory и файловых)."""
    
    @abstractmethod
    def insert(self, table_name: str, **kwargs) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def get_by_id(self, table_name: str, record_id: int) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def filter(self, table_name: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def get_all(self, table_name: str) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def update(self, table_name: str, record_id: int, **updates) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def delete(self, table_name: str, record_id: int) -> None:
        pass
    
    @abstractmethod
    def create_table(self, table_name: str, schema: Dict[str, type]) -> None:
        pass
    
    @abstractmethod
    def list_tables(self) -> List[str]:
        pass
    
    @abstractmethod
    def drop_table(self, table_name: str) -> None:
        pass
    
    @abstractmethod
    def table_exists(self, table_name: str) -> bool:
        pass


class InMemoryDatabase(DatabaseInterface):
    """In-memory реализация БД (из task3)."""
    
    def __init__(self, name: str = "main_db"):
        self.name = name
        self._tables: Dict[str, Dict] = {}
        self._next_ids: Dict[str, int] = {}
        self._schemas: Dict[str, Dict[str, type]] = {}
    
    def _validate_record(self, table_name: str, data: Dict[str, Any]) -> None:
        """Валидация данных по схеме таблицы."""
        schema = self._schemas.get(table_name, {})
        for field, field_type in schema.items():
            if field not in data:
                raise ValidationError(f"Отсутствует поле: {field}")
            if not isinstance(data[field], field_type):
                raise ValidationError(
                    f"Поле '{field}' должно быть {field_type.__name__}"
                )
    
    def create_table(self, table_name: str, schema: Dict[str, type]) -> None:
        if table_name in self._tables:
            raise DatabaseError(f"Таблица '{table_name}' уже существует")
        self._tables[table_name] = {}
        self._next_ids[table_name] = 1
        self._schemas[table_name] = schema
    
    def insert(self, table_name: str, **kwargs) -> Dict[str, Any]:
        if not self.table_exists(table_name):
            raise DatabaseError(f"Таблица '{table_name}' не существует")
        
        self._validate_record(table_name, kwargs)
        
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
        if not self.table_exists(table_name):
            raise DatabaseError(f"Таблица '{table_name}' не существует")
        if record_id not in self._tables[table_name]:
            raise RecordNotFoundError(f"Запись id={record_id} не найдена")
        return self._tables[table_name][record_id]
    
    def filter(self, table_name: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
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
    
    def get_all(self, table_name: str) -> List[Dict[str, Any]]:
        if not self.table_exists(table_name):
            raise DatabaseError(f"Таблица '{table_name}' не существует")
        return list(self._tables[table_name].values())
    
    def update(self, table_name: str, record_id: int, **updates) -> Dict[str, Any]:
        if not self.table_exists(table_name):
            raise DatabaseError(f"Таблица '{table_name}' не существует")
        if record_id not in self._tables[table_name]:
            raise RecordNotFoundError(f"Запись id={record_id} не найдена")
        
        # Валидация обновляемых полей
        schema = self._schemas[table_name]
        for field, value in updates.items():
            if field in schema:
                if not isinstance(value, schema[field]):
                    raise ValidationError(f"Поле '{field}' должно быть {schema[field].__name__}")
        
        self._tables[table_name][record_id].update(updates)
        self._tables[table_name][record_id]["updated_at"] = datetime.now().isoformat()
        return self._tables[table_name][record_id]
    
    def delete(self, table_name: str, record_id: int) -> None:
        if not self.table_exists(table_name):
            raise DatabaseError(f"Таблица '{table_name}' не существует")
        if record_id not in self._tables[table_name]:
            raise RecordNotFoundError(f"Запись id={record_id} не найдена")
        del self._tables[table_name][record_id]
    
    def list_tables(self) -> List[str]:
        return list(self._tables.keys())
    
    def drop_table(self, table_name: str) -> None:
        if not self.table_exists(table_name):
            raise DatabaseError(f"Таблица '{table_name}' не существует")
        del self._tables[table_name]
        del self._next_ids[table_name]
        del self._schemas[table_name]
    
    def table_exists(self, table_name: str) -> bool:
        return table_name in self._tables
    
    def sort(self, table_name: str, field: str, reverse: bool = False) -> List[Dict[str, Any]]:
        """Сортировка записей по полю."""
        if not self.table_exists(table_name):
            raise DatabaseError(f"Таблица '{table_name}' не существует")
        
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


class FileDatabaseJSON(DatabaseInterface):
    """Файловая БД с хранением в JSON."""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self._data: Dict[str, Dict] = {}
        self._schemas: Dict[str, Dict[str, type]] = {}
        self._next_ids: Dict[str, int] = {}
        self._load()
    
    def _load(self):
        """Загрузка данных из JSON файла."""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    self._data = loaded.get("tables", {})
                    self._next_ids = loaded.get("next_ids", {})
                    # Восстановление схем из типов (храним как строки)
                    schemas_raw = loaded.get("schemas", {})
                    self._schemas = {}
                    for table_name, schema_raw in schemas_raw.items():
                        self._schemas[table_name] = {}
                        for field, type_str in schema_raw.items():
                            if type_str == "str":
                                self._schemas[table_name][field] = str
                            elif type_str == "int":
                                self._schemas[table_name][field] = int
                            elif type_str == "float":
                                self._schemas[table_name][field] = float
            except (json.JSONDecodeError, FileNotFoundError) as e:
                raise DatabaseError(f"Ошибка загрузки файла {self.filepath}: {e}")
    
    def _save(self):
        """Сохранение данных в JSON файл."""
        try:
            # Конвертируем типы схем в строки для JSON
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
    
    def _validate_record(self, table_name: str, data: Dict[str, Any]) -> None:
        schema = self._schemas.get(table_name, {})
        for field, field_type in schema.items():
            if field not in data:
                raise ValidationError(f"Отсутствует поле: {field}")
            if not isinstance(data[field], field_type):
                raise ValidationError(
                    f"Поле '{field}' должно быть {field_type.__name__}"
                )
    
    def create_table(self, table_name: str, schema: Dict[str, type]) -> None:
        if table_name in self._data:
            raise DatabaseError(f"Таблица '{table_name}' уже существует")
        self._data[table_name] = {}
        self._next_ids[table_name] = 1
        self._schemas[table_name] = schema
        self._save()
    
    def insert(self, table_name: str, **kwargs) -> Dict[str, Any]:
        if not self.table_exists(table_name):
            raise DatabaseError(f"Таблица '{table_name}' не существует")
        
        self._validate_record(table_name, kwargs)
        
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
        if not self.table_exists(table_name):
            raise DatabaseError(f"Таблица '{table_name}' не существует")
        if str(record_id) not in self._data[table_name]:
            raise RecordNotFoundError(f"Запись id={record_id} не найдена")
        return self._data[table_name][str(record_id)]
    
    def filter(self, table_name: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
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
    
    def get_all(self, table_name: str) -> List[Dict[str, Any]]:
        if not self.table_exists(table_name):
            raise DatabaseError(f"Таблица '{table_name}' не существует")
        return list(self._data[table_name].values())
    
    def update(self, table_name: str, record_id: int, **updates) -> Dict[str, Any]:
        if not self.table_exists(table_name):
            raise DatabaseError(f"Таблица '{table_name}' не существует")
        if str(record_id) not in self._data[table_name]:
            raise RecordNotFoundError(f"Запись id={record_id} не найдена")
        
        schema = self._schemas[table_name]
        for field, value in updates.items():
            if field in schema:
                if not isinstance(value, schema[field]):
                    raise ValidationError(f"Поле '{field}' должно быть {schema[field].__name__}")
        
        self._data[table_name][str(record_id)].update(updates)
        self._data[table_name][str(record_id)]["updated_at"] = datetime.now().isoformat()
        self._save()
        return self._data[table_name][str(record_id)]
    
    def delete(self, table_name: str, record_id: int) -> None:
        if not self.table_exists(table_name):
            raise DatabaseError(f"Таблица '{table_name}' не существует")
        if str(record_id) not in self._data[table_name]:
            raise RecordNotFoundError(f"Запись id={record_id} не найдена")
        del self._data[table_name][str(record_id)]
        self._save()
    
    def list_tables(self) -> List[str]:
        return list(self._data.keys())
    
    def drop_table(self, table_name: str) -> None:
        if not self.table_exists(table_name):
            raise DatabaseError(f"Таблица '{table_name}' не существует")
        del self._data[table_name]
        del self._next_ids[table_name]
        del self._schemas[table_name]
        self._save()
    
    def table_exists(self, table_name: str) -> bool:
        return table_name in self._data
    
    def sort(self, table_name: str, field: str, reverse: bool = False) -> List[Dict[str, Any]]:
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


class FileDatabaseCSV(DatabaseInterface):
    """Файловая БД с хранением в CSV (дополнительная задача)."""
    
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
    
    def _load_all(self):
        """Загрузка всех таблиц из CSV файлов."""
        os.makedirs(self.directory, exist_ok=True)
        
        for filename in os.listdir(self.directory):
            if filename.endswith(".csv"):
                table_name = filename[:-4]
                self._load_table(table_name)
    
    def _load_table(self, table_name: str):
        """Загрузка одной таблицы из CSV."""
        csv_path = self._get_table_path(table_name)
        schema_path = self._get_schema_path(table_name)
        
        # Загрузка схемы
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
        
        # Загрузка данных из CSV
        self._tables[table_name] = []
        max_id = 0
        
        if os.path.exists(csv_path):
            try:
                with open(csv_path, 'r', encoding='utf-8', newline='') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # Конвертация типов
                        if table_name in self._schemas:
                            for field, field_type in self._schemas[table_name].items():
                                if field in row and row[field]:
                                    if field_type == int:
                                        row[field] = int(row[field])
                                    elif field_type == float:
                                        row[field] = float(row[field])
                        self._tables[table_name].append(row)
                        if int(row.get("id", 0)) > max_id:
                            max_id = int(row["id"])
            except Exception as e:
                raise DatabaseError(f"Ошибка загрузки CSV {table_name}: {e}")
        
        self._next_ids[table_name] = max_id + 1
    
    def _save_table(self, table_name: str):
        """Сохранение таблицы в CSV."""
        csv_path = self._get_table_path(table_name)
        schema_path = self._get_schema_path(table_name)
        
        # Сохранение схемы
        if table_name in self._schemas:
            schemas_for_save = {}
            for field, field_type in self._schemas[table_name].items():
                schemas_for_save[field] = field_type.__name__
            with open(schema_path, 'w', encoding='utf-8') as f:
                json.dump(schemas_for_save, f, ensure_ascii=False, indent=2)
        
        # Сохранение данных
        if self._tables.get(table_name):
            fieldnames = list(self._tables[table_name][0].keys())
            with open(csv_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self._tables[table_name])
    
    def create_table(self, table_name: str, schema: Dict[str, type]) -> None:
        if table_name in self._tables:
            raise DatabaseError(f"Таблица '{table_name}' уже существует")
        self._tables[table_name] = []
        self._next_ids[table_name] = 1
        self._schemas[table_name] = schema
        self._save_table(table_name)
    
    def insert(self, table_name: str, **kwargs) -> Dict[str, Any]:
        if not self.table_exists(table_name):
            raise DatabaseError(f"Таблица '{table_name}' не существует")
        
        # Валидация
        schema = self._schemas.get(table_name, {})
        for field, field_type in schema.items():
            if field not in kwargs:
                raise ValidationError(f"Отсутствует поле: {field}")
            if not isinstance(kwargs[field], field_type):
                raise ValidationError(f"Поле '{field}' должно быть {field_type.__name__}")
        
        record_id = self._next_ids[table_name]
        record = {
            "id": str(record_id),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            **kwargs
        }
        
        self._tables[table_name].append(record)
        self._next_ids[table_name] += 1
        self._save_table(table_name)
        return record
    
    def get_by_id(self, table_name: str, record_id: int) -> Dict[str, Any]:
        if not self.table_exists(table_name):
            raise DatabaseError(f"Таблица '{table_name}' не существует")
        for record in self._tables[table_name]:
            if int(record["id"]) == record_id:
                return record
        raise RecordNotFoundError(f"Запись id={record_id} не найдена")
    
    def filter(self, table_name: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
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
                results = [r for r in results if int(r.get(field, 0)) > filter_value]
            elif operator == "lt":
                results = [r for r in results if int(r.get(field, 0)) < filter_value]
            elif operator == "contains":
                results = [r for r in results if filter_value.lower() in str(r.get(field, "")).lower()]
            elif operator == "startswith":
                results = [r for r in results if str(r.get(field, "")).lower().startswith(filter_value.lower())]
            else:
                raise ValidationError(f"Оператор '{operator}' не поддерживается")
        
        return results
    
    def get_all(self, table_name: str) -> List[Dict[str, Any]]:
        if not self.table_exists(table_name):
            raise DatabaseError(f"Таблица '{table_name}' не существует")
        return self._tables[table_name]
    
    def update(self, table_name: str, record_id: int, **updates) -> Dict[str, Any]:
        if not self.table_exists(table_name):
            raise DatabaseError(f"Таблица '{table_name}' не существует")
        
        for i, record in enumerate(self._tables[table_name]):
            if int(record["id"]) == record_id:
                schema = self._schemas[table_name]
                for field, value in updates.items():
                    if field in schema:
                        if not isinstance(value, schema[field]):
                            raise ValidationError(f"Поле '{field}' должно быть {schema[field].__name__}")
                
                self._tables[table_name][i].update(updates)
                self._tables[table_name][i]["updated_at"] = datetime.now().isoformat()
                self._save_table(table_name)
                return self._tables[table_name][i]
        
        raise RecordNotFoundError(f"Запись id={record_id} не найдена")
    
    def delete(self, table_name: str, record_id: int) -> None:
        if not self.table_exists(table_name):
            raise DatabaseError(f"Таблица '{table_name}' не существует")
        
        for i, record in enumerate(self._tables[table_name]):
            if int(record["id"]) == record_id:
                del self._tables[table_name][i]
                self._save_table(table_name)
                return
        
        raise RecordNotFoundError(f"Запись id={record_id} не найдена")
    
    def list_tables(self) -> List[str]:
        return list(self._tables.keys())
    
    def drop_table(self, table_name: str) -> None:
        if not self.table_exists(table_name):
            raise DatabaseError(f"Таблица '{table_name}' не существует")
        
        del self._tables[table_name]
        del self._next_ids[table_name]
        del self._schemas[table_name]
        
        # Удаление файлов
        csv_path = self._get_table_path(table_name)
        schema_path = self._get_schema_path(table_name)
        if os.path.exists(csv_path):
            os.remove(csv_path)
        if os.path.exists(schema_path):
            os.remove(schema_path)
    
    def table_exists(self, table_name: str) -> bool:
        return table_name in self._tables
    
    def sort(self, table_name: str, field: str, reverse: bool = False) -> List[Dict[str, Any]]:
        results = self.get_all(table_name)
        
        def get_sort_key(record):
            value = record.get(field)
            if value is None:
                return (1, None)
            if isinstance(value, str):
                return (0, value.lower())
            if field in self._schemas.get(table_name, {}):
                if self._schemas[table_name][field] in (int, float):
                    value = int(value) if value else 0
            return (0, value)
        
        results.sort(key=get_sort_key, reverse=reverse)
        return results


# Доступные схемы таблиц
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