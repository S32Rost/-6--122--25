"""Console interface for the database."""

from src.database.in_memory import InMemoryDatabase
from src.database.file_json import FileDatabaseJSON
from src.database.file_csv import FileDatabaseCSV
from src.database.schemas import SCHEMAS
from src.database.errors import DatabaseError, RecordNotFoundError, ValidationError


class DatabaseCLI:
    """Console interface for database operations."""
    
    def __init__(self):
        self.db = None
        self.current_table = None
        self._choose_database_type()
        self._init_demo_data()
    
    def _choose_database_type(self):
        """Choose database type."""
        print("\n" + "=" * 50)
        print("ВЫБОР ТИПА БАЗЫ ДАННЫХ")
        print("=" * 50)
        print("1. In-Memory (данные не сохраняются)")
        print("2. File (JSON) - данные сохраняются в JSON файл")
        print("3. File (CSV) - данные сохраняются в CSV файлы")
        print("=" * 50)
        
        while True:
            choice = input("Выберите тип БД (1-3): ").strip()
            
            if choice == "1":
                self.db = InMemoryDatabase("main_db")
                print("✅ Выбрана In-Memory БД")
                break
            elif choice == "2":
                filepath = input("Путь к JSON файлу (по умолчанию: data/db.json): ").strip()
                if not filepath:
                    filepath = "data/db.json"
                self.db = FileDatabaseJSON(filepath)
                print(f"✅ Выбрана JSON БД: {filepath}")
                break
            elif choice == "3":
                directory = input("Папка для CSV (по умолчанию: data/csv_db): ").strip()
                if not directory:
                    directory = "data/csv_db"
                self.db = FileDatabaseCSV(directory)
                print(f"✅ Выбрана CSV БД: {directory}")
                break
            else:
                print("❌ Неверный выбор. Введите 1, 2 или 3.")
    
    def _init_demo_data(self):
        """Initialize demo tables if not exists."""
        if not self.db.table_exists("students"):
            self.db.create_table("students", SCHEMAS["students"])
            self.db.insert("students", name="Иван Петров", age=20, major="Информатика", email="ivan@example.com")
            self.db.insert("students", name="Мария Сидорова", age=19, major="Математика", email="maria@example.com")
            self.db.insert("students", name="Алексей Иванов", age=22, major="Физика", email="alex@example.com")
            self.db.insert("students", name="Анна Козлова", age=21, major="Информатика", email="anna@example.com")
            print("✅ Создана таблица 'students' с демо-данными")
        
        if not self.db.table_exists("books"):
            self.db.create_table("books", SCHEMAS["books"])
            self.db.insert("books", title="Война и мир", author="Толстой Л.Н.", year=1869, isbn="978-5-17-113922-7")
            print("✅ Создана таблица 'books' с демо-данными")
        
        self.current_table = "students"
    
    def _print_help(self):
        """Print help information."""
        print("\n" + "=" * 50)
        print("ДОСТУПНЫЕ КОМАНДЫ")
        print("=" * 50)
        print("\n--- Управление таблицами ---")
        print("  tables                        - список таблиц")
        print("  use <name>                    - выбрать таблицу")
        print("  create <name> <schema>        - создать таблицу")
        print("  drop <name>                   - удалить таблицу")
        print("\n--- CRUD операции ---")
        print("  add field=value ...           - добавить запись")
        print("  list                          - все записи")
        print("  get <id>                      - запись по ID")
        print("  update <id> field=value ...   - обновить запись")
        print("  delete <id>                   - удалить запись")
        print("\n--- Фильтрация ---")
        print("  filter field=value            - точное совпадение")
        print("  filter field__gt=value        - больше")
        print("  filter field__lt=value        - меньше")
        print("  filter field__contains=value  - содержит")
        print("\n--- Сортировка ---")
        print("  sort <field>                  - по возрастанию")
        print("  sort <field> desc             - по убыванию")
        print("\n--- Прочее ---")
        print("  help                          - справка")
        print("  exit                          - выход")
        print("=" * 50)
    
    def _parse_kwargs(self, args):
        """Parse key=value arguments."""
        kwargs = {}
        for arg in args:
            if '=' not in arg:
                raise ValidationError(f"Неверный формат: {arg}")
            key, value = arg.split('=', 1)
            try:
                if '.' in value:
                    value = float(value)
                else:
                    value = int(value)
            except ValueError:
                pass
            kwargs[key] = value
        return kwargs
    
    def _format_record(self, record):
        """Format record for display."""
        parts = [f"ID: {record['id']}"]
        for key, value in record.items():
            if key not in ['id', 'created_at', 'updated_at']:
                parts.append(f"{key}: {value}")
        return " | ".join(parts)
    
    def _print_records(self, records, title="Записи"):
        """Print list of records."""
        if not records:
            print("Записей не найдено")
            return
        print(f"\n{title} (всего: {len(records)}):")
        print("-" * 60)
        for record in records:
            print(self._format_record(record))
        print("-" * 60)
    
    def run(self):
        """Main application loop."""
        print("\n" + "=" * 50)
        print("   DATABASE v4.0 (In-Memory/JSON/CSV)")
        print("=" * 50)
        print(f"Текущая таблица: {self.current_table}")
        self._print_help()
        
        while True:
            try:
                prompt = f"📁 {self.current_table}> " if self.current_table else "📁 > "
                user_input = input(prompt).strip()
                if not user_input:
                    continue
                
                parts = user_input.split()
                command = parts[0].lower()
                
                if command == "exit":
                    print("До свидания!")
                    break
                elif command == "help":
                    self._print_help()
                elif command == "tables":
                    tables = self.db.list_tables()
                    if tables:
                        for t in tables:
                            marker = " ✓" if self.current_table == t else ""
                            print(f"  - {t}{marker}")
                    else:
                        print("Нет таблиц")
                elif command == "use":
                    if len(parts) != 2:
                        print("Использование: use <table_name>")
                        continue
                    if not self.db.table_exists(parts[1]):
                        print(f"Таблица '{parts[1]}' не существует")
                        continue
                    self.current_table = parts[1]
                    print(f"✅ Текущая таблица: {self.current_table}")
                elif command == "create":
                    if len(parts) < 3:
                        print("Использование: create <name> <schema>")
                        print("Схемы: students, books, employees")
                        continue
                    if parts[2] not in SCHEMAS:
                        print(f"Доступные схемы: {', '.join(SCHEMAS.keys())}")
                        continue
                    self.db.create_table(parts[1], SCHEMAS[parts[2]])
                    print(f"✅ Таблица '{parts[1]}' создана")
                elif command == "drop":
                    if len(parts) != 2:
                        print("Использование: drop <table_name>")
                        continue
                    confirm = input(f"Удалить '{parts[1]}'? (yes/no): ")
                    if confirm.lower() == "yes":
                        self.db.drop_table(parts[1])
                        if self.current_table == parts[1]:
                            self.current_table = None
                        print(f"✅ Таблица '{parts[1]}' удалена")
                elif not self.current_table:
                    print("❌ Сначала выберите таблицу: use <name>")
                elif command == "add":
                    kwargs = self._parse_kwargs(parts[1:])
                    record = self.db.insert(self.current_table, **kwargs)
                    print(f"✅ Добавлена: {self._format_record(record)}")
                elif command == "list":
                    records = self.db.get_all(self.current_table)
                    self._print_records(records, f"Таблица '{self.current_table}'")
                elif command == "get":
                    if len(parts) != 2:
                        print("Использование: get <id>")
                        continue
                    record = self.db.get_by_id(self.current_table, int(parts[1]))
                    print(self._format_record(record))
                elif command == "update":
                    if len(parts) < 3:
                        print("Использование: update <id> field=value ...")
                        continue
                    record_id = int(parts[1])
                    updates = self._parse_kwargs(parts[2:])
                    record = self.db.update(self.current_table, record_id, **updates)
                    print(f"✅ Обновлено: {self._format_record(record)}")
                elif command == "delete":
                    if len(parts) != 2:
                        print("Использование: delete <id>")
                        continue
                    self.db.delete(self.current_table, int(parts[1]))
                    print("✅ Запись удалена")
                elif command == "filter":
                    if len(parts) < 2:
                        print("Использование: filter field=value или field__gt=value")
                        continue
                    filters = self._parse_kwargs(parts[1:])
                    results = self.db.filter(self.current_table, filters)
                    self._print_records(results, "Результаты фильтрации")
                elif command == "sort":
                    if len(parts) < 2:
                        print("Использование: sort <field> [desc]")
                        continue
                    field = parts[1]
                    reverse = len(parts) >= 3 and parts[2].lower() == "desc"
                    results = self.db.sort(self.current_table, field, reverse)
                    order = "убыванию" if reverse else "возрастанию"
                    self._print_records(results, f"Сортировка по '{field}' (по {order})")
                else:
                    print(f"❌ Неизвестная команда: {command}")
            
            except (ValidationError, RecordNotFoundError, DatabaseError) as e:
                print(f"❌ Ошибка: {e}")
            except KeyboardInterrupt:
                print("\nДо свидания!")
                break
            except Exception as e:
                print(f"❌ Ошибка: {e}")


def main():
    cli = DatabaseCLI()
    cli.run()


if __name__ == "__main__":
    main()
