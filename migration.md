## Шаги миграции проекта
***

## Шаги миграции

### Шаг 1: Очистка старого виртуального окружения

```bash
cd kanban-tracker

# Деактивировать текущее venv, если активно
deactivate

# Удалить старое виртуальное окружение
rm -rf .venv

# Удалить старые __pycache__
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
```

### Шаг 2: Обновление конфигурации Docker

Проект теперь использует две отдельные базы PostgreSQL (по одной для main-app и auth-service) вместо одной общей.
Что нужно сделать:

1. Остановить и удалить старый(ые) контейнер(ы) базы данных из прошлой конфигурации.
2. Удалить связанные тома, чтобы начать с чистой базы.
3. Запустить новую конфигурацию с обновлённым файлом `docker-compose.yml`.

### Шаг 3: Настройка Main App

```bash
# Перейти в директорию приложения
cd services/main-app

# Установить зависимости через Poetry
poetry install

# Запустить миграции
poetry run alembic upgrade head

# Проверить текущую миграцию
poetry run alembic current
```

### Шаг 4: Настройка PyCharm

#### 4.1 Обновление интерпретатора Python

1. Открыть: PyCharm → Settings → Project → Python Interpreter.
2. Удалить старый интерпретатор.
3. Добавить новый интерпретатор:
   - Нажать ⚙️ → Add.
   - Выбрать "Poetry Environment".
   - Base interpreter: Python 3.13.
   - Poetry executable: автоопределение (по умолчанию).
   - Нажать OK.

#### 4.2 Отметка Sources Root

1. Правый клик по `services/main-app/src` → Mark Directory as → Sources Root (директория src должна стать синей).
2. Аналогично отметить директорию источников для приложения авторизации `auth`.
