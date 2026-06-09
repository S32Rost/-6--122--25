import sys
import os
from database import InMemoryDatabase, FileDatabaseJSON, FileDatabaseCSV, SCHEMAS
from errors import DatabaseError, RecordNotFoundError, ValidationError


class DatabaseCLI:
    """Консольный интерфейс для работы с БД."""
    
    def __init__(self):
        self.db = None
        self.current_table = None
        self._choose_database_type()
        self._init_demo_data()
    
    def _choose_database_type(self):
        """Выбор типа базы данных."""
        print("\n" + "=" * 50)
        print("ВЫБОР ТИПА БАЗЫ ДАННЫХ")
        print("=" * 50)
        print("1. In-Memory (данные не сохраняются)")
        print("2. File (JSON) - данные сохраняются в JSON файл")
        print("3. File (CSV) - данные сохраняются в CSV файлы (ДОП. ЗАДАНИЕ)")
        print("=" * 50)
        
        while True:
            choice = input("Выберите тип БД (1-3): ").strip()
            
            if choice == "1":
                self.db = InMemoryDatabase("main_db")
                print("✅ Выбрана In-Memory БД (данные не сохраняются после выхода)")
                break
            elif choice == "2":
                filepath = input("Введите путь к JSON файлу (по умолчанию: data/db.json): ").strip()
                if not filepath:
                    filepath = "data/db.json"
                self.db = FileDatabaseJSON(filepath)
                print(f"✅ Выбрана файловая БД (JSON): {filepath}")
                break
            elif choice == "3":
                directory = input("Введите папку для CSV файлов (по умолчанию: data/csv_db): ").strip()
                if not directory:
                    directory = "data/csv_db"
                self.db = FileDatabaseCSV(directory)
                print(f"✅ Выбрана файловая БД (CSV): {directory}")
                break
            else:
                print("❌ Неверный выбор. Введите 1, 2 или 3.")
    
    def _init_demo_data(self):
        """Инициализация демонстрационных данных (только если таблиц нет)."""
        if not self.db.table_exists("students"):
            self.db.create_table("students", SCHEMAS["students"])
            table = self.db
            table.insert("students", name="Иван Петров", age=20, major="Информатика", email="ivan@example.com")
            table.insert("students", name="Мария Сидорова", age=19, major="Математика", email="maria@example.com")
            table.insert("students", name="Алексей Иванов", age=22, major="Физика", email="alex@example.com")
            table.insert("students", name="Анна Козлова", age=21, major="Информатика", email="anna@example.com")
            table.insert("students", name="Дмитрий Соколов", age=20, major="Программирование", email="dmitry@example.com")
            print("✅ Создана таблица 'students' с демо-данными")
        
        if not self.db.table_exists("books"):
            self.db.create_table("books", SCHEMAS["books"])
            table = self.db
            table.insert("books", title="Война и мир", author="Толстой Л.Н.", year=1869, isbn="978-5-17-113922-7")
            table.insert("books", title="Преступление и наказание", author="Достоевский Ф.М.", year=1866, isbn="978-5-04-098349-7")
            print("✅ Создана таблица 'books' с демо-данными")
        
        self.current_table = "students"
    
    def _print_help(self):
        """Вывод справки."""
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
        print("  filter field__startswith=val  - начинается с")
        
        print("\n--- Сортировка ---")
        print("  sort <field>                  - сортировка по возрастанию")
        print("  sort <field> desc             - сортировка по убыванию")
        
        print("\n--- Прочее ---")
        print("  help                          - справка")
        print("  exit                          - выход")
        print("=" * 50 + "\n")
    
    def _parse_kwargs(self, args):
        """Разбор аргументов в формате key=value."""
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
    
    def _parse_filters(self, args):
        """Разбор фильтров с операторами."""
        filters = {}
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
            filters[key] = value
        return filters
    
    def _format_record(self, record, show_metadata=True):
        """Форматирование записи для вывода."""
        output = f"ID: {record['id']}"
        for key, value in record.items():
            if key not in ['id', 'created_at', 'updated_at']:
                output += f" | {key}: {value}"
        return output
    
    def _print_records(self, records, title="Записи"):
        """Вывод списка записей."""
        if not records:
            print("Записей не найдено")
            return
        print(f"\n{title} (всего: {len(records)}):")
        print("-" * 80)
        for record in records:
            print(self._format_record(record))
        print("-" * 80)
    
    def run(self):
        """Основной цикл приложения."""
        print("\n" + "=" * 50)
        print("   IN-MEMORY/FILE DATABASE v4.0")
        print("   с поддержкой JSON и CSV")
        print("=" * 50)
        print(f"Текущая таблица: {self.current_table}")
        self._print_help()
        
        while True:
            try:
                if self.current_table:
                    db_type = type(self.db).__name__
                    prompt = f"📁 {db_type}/{self.current_table}> "
                else:
                    prompt = f"📁 > "
                
                user_input = input(prompt).strip()
                if not user_input:
                    continue
                
                parts = user_input.split()
                command = parts[0].lower()
                
                # Глобальные команды
                if command == "exit":
                    print("До свидания!")
                    break
                elif command == "help":
                    self._print_help()
                elif command == "tables":
                    tables = self.db.list_tables()
                    if not tables:
                        print("Нет созданных таблиц")
                    else:
                        print("Таблицы в базе данных:")
                        for t in tables:
                            marker = " ✓" if self.current_table == t else ""
                            print(f"  - {t}{marker}")
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
                        print("Доступные схемы: students, books, employees")
                        continue
                    schema_name = parts[2]
                    if schema_name not in SCHEMAS:
                        print(f"Доступные схемы: {', '.join(SCHEMAS.keys())}")
                        continue
                    self.db.create_table(parts[1], SCHEMAS[schema_name])
                    print(f"✅ Таблица '{parts[1]}' создана (схема: {schema_name})")
                elif command == "drop":
                    if len(parts) != 2:
                        print("Использование: drop <table_name>")
                        continue
                    confirm = input(f"⚠️ Удалить таблицу '{parts[1]}'? (yes/no): ")
                    if confirm.lower() == "yes":
                        self.db.drop_table(parts[1])
                        if self.current_table == parts[1]:
                            self.current_table = None
                        print(f"✅ Таблица '{parts[1]}' удалена")
                elif not self.current_table:
                    print("❌ Сначала выберите таблицу: use <table_name>")
                
                # Команды с текущей таблицей
                else:
                    if command == "add":
                        if len(parts) < 2:
                            print("Использование: add field1=value1 field2=value2 ...")
                            continue
                        kwargs = self._parse_kwargs(parts[1:])
                        record = self.db.insert(self.current_table, **kwargs)
                        print(f"✅ Запись добавлена:")
                        print(self._format_record(record))
                    
                    elif command == "list":
                        records = self.db.get_all(self.current_table)
                        self._print_records(records, f"Таблица '{self.current_table}'")
                    
                    elif command == "get":
                        if len(parts) != 2:
                            print("Использование: get <id>")
                            continue
                        try:
                            record_id = int(parts[1])
                            record = self.db.get_by_id(self.current_table, record_id)
                            print(self._format_record(record))
                        except ValueError:
                            print("Ошибка: ID должен быть числом")
                    
                    elif command == "update":
                        if len(parts) < 3:
                            print("Использование: update <id> field1=value1 ...")
                            continue
                        try:
                            record_id = int(parts[1])
                            updates = self._parse_kwargs(parts[2:])
                            record = self.db.update(self.current_table, record_id, **updates)
                            print(f"✅ Запись обновлена:")
                            print(self._format_record(record))
                        except ValueError:
                            print("Ошибка: ID должен быть числом")
                    
                    elif command == "delete":
                        if len(parts) != 2:
                            print("Использование: delete <id>")
                            continue
                        try:
                            record_id = int(parts[1])
                            self.db.delete(self.current_table, record_id)
                            print(f"✅ Запись с id={record_id} удалена")
                        except ValueError:
                            print("Ошибка: ID должен быть числом")
                    
                    elif command == "filter":
                        if len(parts) < 2:
                            print("Использование: filter field=value или field__operator=value")
                            continue
                        filters = self._parse_filters(parts[1:])
                        results = self.db.filter(self.current_table, filters)
                        self._print_records(results, "Результаты фильтрации")
                    
                    elif command == "sort":
                        if len(parts) < 2:
                            print("Использование: sort <field> [desc]")
                            continue
                        
                        field = parts[1]
                        reverse = False
                        if len(parts) >= 3 and parts[2].lower() == "desc":
                            reverse = True
                        
                        results = self.db.sort(self.current_table, field, reverse)
                        order_text = "убыванию" if reverse else "возрастанию"
                        self._print_records(results, f"Сортировка по полю '{field}' (по {order_text})")
                    
                    else:
                        print(f"❌ Неизвестная команда: {command}")
                        print("Введите 'help' для списка команд")
            
            except (ValidationError, RecordNotFoundError, DatabaseError) as e:
                print(f"❌ Ошибка: {e}")
            except KeyboardInterrupt:
                print("\nДо свидания!")
                break
            except Exception as e:
                print(f"❌ Неожиданная ошибка: {e}")


if __name__ == "__main__":
    cli = DatabaseCLI()
    cli.run()