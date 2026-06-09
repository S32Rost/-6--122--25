import sys
from database import Database, SCHEMAS
from errors import DatabaseError, RecordNotFoundError, ValidationError

class DatabaseCLI:
    """Консольный интерфейс для работы с БД (ООП реализация)."""
    
    def __init__(self):
        self.db = Database()
        self.current_table = None
        self._init_demo_data()
    
    def _init_demo_data(self):
        """Инициализация демонстрационных данных."""
        if not self.db.table_exists("students"):
            self.db.create_table("students", SCHEMAS["students"])
            table = self.db.get_table("students")
            table.insert(name="Иван Петров", age=20, major="Информатика", email="ivan@example.com")
            table.insert(name="Мария Сидорова", age=19, major="Математика", email="maria@example.com")
            table.insert(name="Алексей Иванов", age=22, major="Физика", email="alex@example.com")
            table.insert(name="Анна Козлова", age=21, major="Информатика", email="anna@example.com")
            table.insert(name="Дмитрий Соколов", age=20, major="Программирование", email="dmitry@example.com")
        
        if not self.db.table_exists("books"):
            self.db.create_table("books", SCHEMAS["books"])
            table = self.db.get_table("books")
            table.insert(title="Война и мир", author="Толстой Л.Н.", year=1869, isbn="978-5-17-113922-7")
            table.insert(title="Преступление и наказание", author="Достоевский Ф.М.", year=1866, isbn="978-5-04-098349-7")
            table.insert(title="Анна Каренина", author="Толстой Л.Н.", year=1877, isbn="978-5-17-118888-1")
        
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
        print("  Пример: sort age")
        print("  Пример: sort name desc")
        
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
        if show_metadata:
            created = record['created_at'].strftime('%H:%M:%S') if hasattr(record['created_at'], 'strftime') else record['created_at']
            updated = record['updated_at'].strftime('%H:%M:%S') if hasattr(record['updated_at'], 'strftime') else record['updated_at']
            output += f" [созд:{created} обн:{updated}]"
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
        print("   IN-MEMORY DATABASE v3.0")
        print("   с поддержкой сортировки")
        print("=" * 50)
        print(f"Текущая таблица: {self.current_table}")
        self._print_help()
        
        while True:
            try:
                if self.current_table:
                    prompt = f"📁 {self.db.name}/{self.current_table}> "
                else:
                    prompt = f"📁 {self.db.name}> "
                
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
                    table = self.db.get_table(self.current_table)
                    
                    if command == "add":
                        if len(parts) < 2:
                            print("Использование: add field1=value1 field2=value2 ...")
                            continue
                        kwargs = self._parse_kwargs(parts[1:])
                        record = table.insert(**kwargs)
                        print(f"✅ Запись добавлена:")
                        print(self._format_record(record))
                    
                    elif command == "list":
                        records = table.get_all()
                        self._print_records(records, f"Таблица '{self.current_table}'")
                    
                    elif command == "get":
                        if len(parts) != 2:
                            print("Использование: get <id>")
                            continue
                        try:
                            record_id = int(parts[1])
                            record = table.get_by_id(record_id)
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
                            record = table.update(record_id, **updates)
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
                            table.delete(record_id)
                            print(f"✅ Запись с id={record_id} удалена")
                        except ValueError:
                            print("Ошибка: ID должен быть числом")
                    
                    elif command == "filter":
                        if len(parts) < 2:
                            print("Использование: filter field=value или field__operator=value")
                            continue
                        filters = self._parse_filters(parts[1:])
                        results = table.filter(filters)
                        self._print_records(results, "Результаты фильтрации")
                    
                    elif command == "sort":
                        if len(parts) < 2:
                            print("Использование: sort <field> [desc]")
                            print("Примеры:")
                            print("  sort age          - по возрастанию")
                            print("  sort age desc     - по убыванию")
                            print("  sort name         - по имени (А-Я)")
                            print("  sort name desc    - по имени (Я-А)")
                            continue
                        
                        field = parts[1]
                        reverse = False
                        if len(parts) >= 3 and parts[2].lower() == "desc":
                            reverse = True
                        
                        try:
                            results = table.sort(field, reverse)
                            order_text = "убыванию" if reverse else "возрастанию"
                            self._print_records(results, f"Сортировка по полю '{field}' (по {order_text})")
                        except ValidationError as e:
                            print(f"Ошибка: {e}")
                    
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