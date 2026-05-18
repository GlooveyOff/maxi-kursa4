# EduPlatform Backend

Backend для образовательной онлайн-платформы с курсами. Курсовая работа,
тема — «Разработка backend-а для веб-сайта образовательной платформы с курсами».

## Возможности

- Регистрация и вход (JWT)
- Профиль пользователя, роль «преподаватель»
- CRUD курсов, категорий, уроков
- Запись студентов на курсы
- Отметка пройденных уроков и подсчёт прогресса
- Отзывы и средний рейтинг курса
- Поиск и фильтры по курсам (название, цена, категория)

## Стек

- Python 3.11+
- FastAPI 0.115
- SQLAlchemy 2 + PostgreSQL
- Pydantic 2
- python-jose (JWT)
- passlib + bcrypt (хэширование паролей)
- pytest (тесты)

## Запуск локально

```bash
# 1. создаём виртуальное окружение
python -m venv .venv
source .venv/bin/activate   # для Windows: .venv\Scripts\activate

# 2. ставим зависимости
pip install -r requirements.txt

# 3. копируем настройки
cp .env.example .env
# при необходимости меняем DATABASE_URL и SECRET_KEY

# 4. запускаем сервер
uvicorn app.main:app --reload
```

После запуска интерактивная документация (Swagger UI) доступна по адресу
http://127.0.0.1:8000/docs

## Запуск через Docker

```bash
docker compose up --build
```

Поднимется PostgreSQL и сам сервер на порту 8000.

## Запуск тестов

```bash
pytest -v
```

## Структура проекта

```
app/
├── main.py            # точка входа, подключение роутеров
├── config.py          # настройки (через pydantic-settings)
├── database.py        # подключение к БД
├── security.py        # хэширование паролей, JWT
├── deps.py            # Depends-зависимости (текущий пользователь и т.п.)
├── models/            # ORM-модели SQLAlchemy
├── schemas/           # pydantic-схемы для запросов/ответов
└── routers/           # эндпоинты по доменам
tests/                 # тесты на pytest
```
