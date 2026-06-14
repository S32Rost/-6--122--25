Шитый Ростислав Вячеславович
М6О-122БВ-25
Python


Проект: База данных (In-Memory + File-based)

Описание проекта

Проект представляет собой базу данных с поддержкой трех режимов хранения:
- In-Memory — данные хранятся в оперативной памяти (теряются после выхода)
- File (JSON) — данные сохраняются в JSON файл
- File (CSV) — данные сохраняются в CSV файлы (дополнительное задание)

Реализованы все CRUD операции, фильтрация, сортировка. Проект покрыт тестами (>80%).

Структура проекта
pioa-m60-122bv-25/
│
├── src/database/ Исходный код (9 модулей)
│ ├── init.py
│ ├── interfaces.py Абстрактный интерфейс DatabaseInterface
│ ├── in_memory.py In-Memory реализация
│ ├── file_json.py JSON файловая реализация
│ ├── file_csv.py CSV файловая реализация
│ ├── models.py Модели данных (Student)
│ ├── errors.py Исключения (DatabaseError, RecordNotFoundError, ValidationError)
│ ├── validators.py Валидация данных
│ └── schemas.py Схемы таблиц (students, books, employees)
│
├── tests/ Тесты (52 теста, покрытие >80%)
│ ├── test_in_memory.py 18 тестов
│ ├── test_file_json.py 7 тестов
│ ├── test_file_csv.py 7 тестов
│ ├── test_models.py 4 теста
│ ├── test_validators.py 10 тестов
│ └── test_errors.py 4 теста
│
├── task2/ История выполнения task2 (только README)
├── task3/ История выполнения task3 (только README)
├── task4/ История выполнения task4 (только README)
│
├── main.py Консольный интерфейс
├── requirements.txt Зависимости (pytest, pytest-cov)
├── .gitignore Игнорирование pycache, *.pyc, data/
└── README.md Документация


Назначение модулей

| Файл | Описание |
|------|----------|
| `src/database/interfaces.py` | Абстрактный класс `DatabaseInterface` с методами CRUD, фильтрации, сортировки |
| `src/database/in_memory.py` | In-Memory реализация (данные теряются после выхода) |
| `src/database/file_json.py` | JSON файловая реализация (данные сохраняются на диск) |
| `src/database/file_csv.py` | CSV файловая реализация (данные сохраняются, можно открыть в Excel) |
| `src/database/models.py` | Модель `Student` (id, name, age, major, enrolled_at) |
| `src/database/errors.py` | Исключения: `DatabaseError`, `RecordNotFoundError`, `ValidationError` |
| `src/database/validators.py` | Валидация имени, возраста, специальности |
| `src/database/schemas.py` | Предопределённые схемы: students, books, employees |
| `main.py` | Консольный интерфейс (выбор типа БД, обработка команд) |

Реализованная функциональность

Управление таблицами

| Команда | Описание | Пример |
|---------|----------|--------|
| `tables` | Показать все таблицы | `tables` |
| `use <name>` | Выбрать активную таблицу | `use students` |
| `create <name> <schema>` | Создать таблицу | `create my_students students` |
| `drop <name>` | Удалить таблицу (с подтверждением) | `drop my_students` |

CRUD операции

| Команда | Описание | Пример |
|---------|----------|--------|
| `add field=value...` | Добавить запись | `add name=Иван age=20 major=Физика email=ivan@test.com` |
| `list` | Показать все записи | `list` |
| `get <id>` | Показать запись по ID | `get 1` |
| `update <id> field=value...` | Обновить запись | `update 1 age=21` |
| `delete <id>` | Удалить запись | `delete 1` |

Фильтрация

| Оператор | Описание | Пример |
|----------|----------|--------|
| `field=value` | Точное совпадение | `filter name=Иван` |
| `field__gt=value` | Больше чем | `filter age__gt=20` |
| `field__lt=value` | Меньше чем | `filter age__lt=30` |
| `field__contains=value` | Содержит подстроку | `filter name__contains=ан` |
| `field__startswith=value` | Начинается с | `filter name__startswith=Ив` |

Сортировка

| Команда | Описание | Пример |
|---------|----------|--------|
| `sort <field>` | Сортировка по возрастанию | `sort age` |
| `sort <field> desc` | Сортировка по убыванию | `sort age desc` |

Доступные схемы таблиц

| Схема | Поля |
|-------|------|
| `students` | name (str), age (int), major (str), email (str) |
| `books` | title (str), author (str), year (int), isbn (str) |
| `employees` | full_name (str), position (str), salary (float), department (str) |

Инструкция по запуску

Требования
- Python 3.10 или выше

Запуск приложения

cd pioa-m60-122bv-25
python main.py

ВЫБОР ТИПА БАЗЫ ДАННЫХ
1. In-Memory (данные не сохраняются)
2. File (JSON) - данные сохраняются в JSON файл
3. File (CSV) - данные сохраняются в CSV файлы

Выберите тип БД (1-3):

Запуск тестов:
Установка зависимостей
pip install -r requirements.txt

Запуск всех тестов
python -m unittest discover tests -v

Запуск конкретного теста
python -m unittest tests.test_in_memory -v

Результаты тестов
Ran 52 tests in 0.060s
OK

Количество тестов по категориям:
- In-Memory: 18
- JSON: 7
- CSV: 7
- Модели: 4
- Валидация: 10
- Исключения: 4
- Итого: 52

Обработка ошибок
- ValidationError - неверные данные (пустые поля, неверный тип, возраст вне диапазона)
- RecordNotFoundError - запись не найдена (при get/update/delete)
- DatabaseError - ошибки БД (таблица не существует, файл повреждён)

Все ошибки перехватываются и выводятся понятным сообщением.

Примечания
- Папки task2/, task3/, task4/ содержат только README для истории выполнения заданий
- Весь актуальный код находится в корне репозитория и в папке src/