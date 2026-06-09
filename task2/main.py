import sys
from database import Database, SCHEMAS
from errors import DatabaseError, RecordNotFoundError, ValidationError

class DatabaseCLI:
    """Консольный интерфейс для работы с БД."""
    
    def __init__(self):
        self.db = Database()
        self.current_table = None
        self._init_demo_data()
    
    def _init_demo_data(self):
        """Создание демо-таблиц."""
        # Создаем таблицу студентов с демо-данными
        if not self.db.table_exists("students"):
            self.db.create_table("students", SCHEMAS["students"])
            students_table = self.db.get_table("students")
            
            # Добавляем тестовые данные
            students_table.insert(name="Иван Петров", age=20, major="Информатика", email="ivan@example.com")
            students_table.insert(name="Мария Сидорова", age=19, major="Математика", email="maria@example.com")
            students_table.insert(name="Алексей Иванов", age=22, major="Физика", email="alex@example.com")
            students_table.insert(name="Анна Козлова", age=21, major="Информатика", email="anna@example.com")
        
        # Создаем таблицу книг
        if not self.db.table_exists("books"):
            self.db.create_table("books", SCHEMAS["books"])
            books_table = self.db.get_table("books")
            books_table.insert(title="Война и мир", author="Толстой Л.Н.", year=1869, isbn="978-5-17-113922-7")
            books_table.insert(title="Преступление и наказание", author="Достоевский Ф.М.", year=1866, isbn="978-5-04-098349-7")
        
        self.current_table = "students"
    
    def _print_record(self, record):
        """Вывод записи в читаемом формате."""
        print(f"ID: {record['id']}")
        for key, value in record.items():
            if key not in ['id', 'created_at', 'updated_at']:
                print(f"  {key}: {value}")
        print(f"  создано: {record['created_at'].strftime('%Y-%m-%d %H:%M')}")
        print(f"  обновлено: {record['updated_at'].strftime('%Y-%m-%d %H:%M')}")
        print("-" * 40)
    
    def _print_help(self):
        print("\n" + "="*50)
        print("ДОСТУПНЫЕ КОМАНДЫ")
        print("="*50)
        print("\n=== Управление таблицами ===")
        print("tables                    - показать все таблицы")
        print("use <table_name>          - выбрать таблицу")
        print("create <name> [schema]    - создать таблицу (schema: students/books/employees)")
        print("drop <table_name>         - удалить таблицу")
        
        print("\n=== CRUD операции (над текущей таблицей) ===")
        print("add field1=value1 field2=value2 ...    - добавить запись")
        print("list                                    - показать все записи")
        print("get <id>                                - показать запись по ID")
        print("update <id> field1=value1 ...           - обновить запись")
        print("delete <id>                             - удалить запись")
        
        print("\n=== Фильтрация ===")
        print("filter field=value                      - точное совпадение")
        print("filter field__gt=value                  - больше чем")
        print("filter field__lt=value                  - меньше чем")
        print("filter field__contains=value            - содержит")
        print("filter field__startswith=value          - начинается с")
        print("Пример: filter age__gt=19 major__contains=мат")
        
        print("\n=== Прочее ===")
        print("help                    - показать эту справку")
        print("exit                    - выход")
        print("="*50 + "\n")
    
    def _parse_kwargs(self, args):
        """Разбор аргументов в формате key=value."""
        kwargs = {}
        for arg in args:
            if '=' not in arg:
                raise ValidationError(f"Неверный формат '{arg}'. Используйте key=value")
            key, value = arg.split('=', 1)
            
            # Пробуем преобразовать в числа, если возможно
            try:
                if '.' in value:
                    value = float(value)
                else:
                    value = int(value)
            except ValueError:
                pass  # оставляем как строку
            
            kwargs[key] = value
        return kwargs
    
    def _parse_filters(self, args):
        """Разбор фильтров с поддержкой операторов."""
        filters = {}
        for arg in args:
            if '=' not in arg:
                raise ValidationError(f"Неверный формат '{arg}'. Используйте field=value или field__operator=value")
            
            key, value = arg.split('=', 1)
            
            # Преобразуем значение
            try:
                if '.' in value:
                    value = float(value)
                else:
                    value = int(value)
            except ValueError:
                pass
            
            filters[key] = value
        return filters
    
    def run(self):
        """Основной цикл приложения."""
        print(f"Добро пожаловать в in-memory базу данных")
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
                
                # Глобальные команды (не требуют выбранной таблицы)
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
                            marker = " *" if self.current_table == t else ""
                            print(f"  - {t}{marker}")
                
                elif command == "create":
                    if len(parts) < 2:
                        print("Использование: create <table_name> [schema]")
                        print("Доступные схемы: students, books, employees")
                        continue
                    
                    table_name = parts[1]
                    schema_name = parts[2] if len(parts) > 2 else "students"
                    
                    if schema_name not in SCHEMAS:
                        print(f"Схема '{schema_name}' не найдена. Доступны: {', '.join(SCHEMAS.keys())}")
                        continue
                    
                    if self.db.table_exists(table_name):
                        print(f"Таблица '{table_name}' уже существует")
                        continue
                    
                    self.db.create_table(table_name, SCHEMAS[schema_name])
                    print(f"✅ Таблица '{table_name}' создана (схема: {schema_name})")
                
                elif command == "drop":
                    if len(parts) != 2:
                        print("Использование: drop <table_name>")
                        continue
                    
                    table_name = parts[1]
                    if not self.db.table_exists(table_name):
                        print(f"Таблица '{table_name}' не существует")
                        continue
                    
                    confirm = input(f"⚠️ Удалить таблицу '{table_name}'? (yes/no): ")
                    if confirm.lower() == "yes":
                        self.db.drop_table(table_name)
                        if self.current_table == table_name:
                            self.current_table = None
                        print(f"✅ Таблица '{table_name}' удалена")
                
                elif command == "use":
                    if len(parts) != 2:
                        print("Использование: use <table_name>")
                        continue
                    
                    table_name = parts[1]
                    if not self.db.table_exists(table_name):
                        print(f"Таблица '{table_name}' не существует")
                        continue
                    
                    self.current_table = table_name
                    print(f"✅ Текущая таблица: {self.current_table}")
                
                # Команды, требующие выбранной таблицы
                elif not self.current_table:
                    print("❌ Сначала выберите таблицу командой 'use <table_name>'")
                
                else:
                    table = self.db.get_table(self.current_table)
                    
                    if command == "add":
                        if len(parts) < 2:
                            print("Использование: add field1=value1 field2=value2 ...")
                            continue
                        
                        kwargs = self._parse_kwargs(parts[1:])
                        record = table.insert(**kwargs)
                        print("✅ Запись добавлена:")
                        self._print_record(record)
                    
                    elif command == "list":
                        records = table.get_all()
                        if not records:
                            print("Нет записей в таблице")
                        else:
                            print(f"Всего записей: {len(records)}")
                            for record in records:
                                self._print_record(record)
                    
                    elif command == "get":
                        if len(parts) != 2:
                            print("Использование: get <id>")
                            continue
                        
                        try:
                            record_id = int(parts[1])
                            record = table.get_by_id(record_id)
                            self._print_record(record)
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
                            print("✅ Запись обновлена:")
                            self._print_record(record)
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
                        
                        if not results:
                            print("Записи не найдены")
                        else:
                            print(f"Найдено записей: {len(results)}")
                            for record in results:
                                self._print_record(record)
                    
                    else:
                        print(f"Неизвестная команда: {command}. Введите 'help' для справки.")
            
            except ValidationError as e:
                print(f"❌ Ошибка валидации: {e}")
            except RecordNotFoundError as e:
                print(f"❌ {e}")
            except DatabaseError as e:
                print(f"❌ Ошибка БД: {e}")
            except (KeyboardInterrupt, EOFError):
                print("\nДо свидания!")
                break
            except Exception as e:
                print(f"❌ Неожиданная ошибка: {e}")


def main():
    cli = DatabaseCLI()
    cli.run()


if __name__ == "__main__":
    main()