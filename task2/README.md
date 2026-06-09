Описание структуры проекта

Расположение модулей и их назначение
task2/
│
├── main.py # Главный модуль, консольный интерфейс пользователя
├── database.py # Ядро БД: классы Database и Table (in-memory)
├── models.py # Модели данных (Student)
├── errors.py # Пользовательские исключения
├── validators.py # Функции валидации данных
└── README.md # Документация проекта


Назначение модулей

- main.py: Содержит класс `DatabaseCLI` — консольный интерфейс пользователя. Обрабатывает ввод команд, вызывает методы БД, выводит результаты. Реализует управление текущей таблицей, парсинг аргументов и фильтров.

- database.py: Содержит два основных класса:
  - `Table` — представляет отдельную таблицу, хранит записи в `dict`, управляет идентификаторами. Реализует операции `insert`, `get_by_id`, `filter`, `get_all`, `update`, `delete`, `sort`, `count`, `clear`.
  - `Database` — управляет несколькими таблицами, позволяет создавать, удалять, переключаться между таблицами. Содержит предопределенные схемы таблиц (`students`, `books`, `employees`).

- models.py: Определяет dataclass `Student` с полями: id, name, age, major, enrolled_at. Содержит методы `to_dict()` для сериализации и `from_dict()` для десериализации.

- errors.py: Кастомные исключения: `DatabaseError` (базовое), `RecordNotFoundError` (запись не найдена), `ValidationError` (ошибка валидации данных).

- validators.py: Функция `validate_student_data` для проверки имени, возраста, специальности.

Описание реализованной функциональности

Управление таблицами

| Команда | Описание | Пример |
|---------|----------|--------|
| `tables` | Показать все таблицы | `tables` |
| `use <name>` | Выбрать таблицу | `use students` |
| `create <name> <schema>` | Создать таблицу | `create my_students students` |
| `drop <name>` | Удалить таблицу | `drop my_students` |

CRUD операции

| Команда | Описание | Пример |
|---------|----------|--------|
| `add field=value...` | Добавить запись | `add name=Иван age=20` |
| `list` | Все записи | `list` |
| `get <id>` | Запись по ID | `get 1` |
| `update <id> field=value` | Обновить | `update 1 age=21` |
| `delete <id>` | Удалить | `delete 1` |

Фильтрация

| Оператор | Описание | Пример |
|----------|----------|--------|
| `field=value` | Точное совпадение | `filter name=Иван` |
| `field__gt=value` | Больше чем | `filter age__gt=20` |
| `field__lt=value` | Меньше чем | `filter age__lt=30` |
| `field__contains=value` | Содержит | `filter name__contains=ан` |
| `field__startswith=value` | Начинается с | `filter name__startswith=Ив` |

Сортировка

| Команда | Описание | Пример |
|---------|----------|--------|
| `sort <field>` | По возрастанию | `sort age` |
| `sort <field> desc` | По убыванию | `sort age desc` |

Доступные схемы таблиц

| Схема | Поля |
|-------|------|
| `students` | name (str), age (int), major (str), email (str) |
| `books` | title (str), author (str), year (int), isbn (str) |
| `employees` | full_name (str), position (str), salary (float), department (str) |

Обработка ошибок

- `ValidationError` — неверные данные (пустые поля, неверный тип)
- `RecordNotFoundError` — запись не найдена
- `DatabaseError` — ошибки БД (таблица не существует)

Инструкция по запуску

Требования
- Python 3.10 или выше

Запуск приложения

cd task2
python main.py
