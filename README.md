![CI](https://github.com/Zdestr/product_roadmap_app/actions/workflows/ci.yml/badge.svg)

```markdown
# Product Roadmap API

Сервис для управления планом развития продукта / учебного курса:

- пользователи (`User`);
- дорожные карты (`Roadmap`);
- этапы (`Milestone`);
- статистика по прогрессу.

Стек:

- Python 3.10+
- FastAPI
- SQLAlchemy
- SQLite / PostgreSQL
- Pytest

---

## Возможности

### Сущности

- **User**
  - Регистрация
  - Логин (JWT)
- **Roadmap**
  - CRUD (создание, чтение, обновление, удаление)
  - Теги и фильтрация по ним
  - Экспорт в JSON / CSV
- **Milestone**
  - CRUD
  - Статусы: `planned`, `in_progress`, `done`, `cancelled`
  - Валидация дат (дедлайн не раньше даты создания roadmap, не в прошлом — см. ниже)
- **Статистика**
  - Общее количество roadmaps
  - Общее количество milestones
  - Количество milestones по статусам
  - Просроченные milestones
  - Ближайшие milestones в пределах 7 дней

### Безопасность

- Аутентификация: JWT (OAuth2 password flow)
- Авторизация:
  - Пользователь видит только свои roadmaps и milestones
  - Попытка доступа к чужим ресурсам возвращает `404`
- Хранение паролей: `pbkdf2_sha256` через Passlib

---

## Структура проекта

```text
product_roadmap_app/
├─ app/
│  ├─ main.py                 # Точка входа FastAPI
│  ├─ core/
│  │  ├─ config.py            # Настройки (DATABASE_URL, SECRET_KEY и т.д.)
│  │  ├─ security.py          # Хэширование паролей, JWT
│  │  └─ __init__.py
│  ├─ db/
│  │  ├─ base.py              # Base = declarative_base()
│  │  ├─ session.py           # engine, SessionLocal, get_db
│  │  └─ __init__.py
│  ├─ models/
│  │  ├─ user.py              # Модель User
│  │  ├─ roadmap.py           # Модель Roadmap
│  │  ├─ milestone.py         # Модель Milestone
│  │  └─ __init__.py          # Импорт всех моделей
│  ├─ schemas/
│  │  ├─ auth.py              # Схемы для токена
│  │  ├─ user.py              # Схемы пользователя
│  │  ├─ roadmap.py           # Схемы дорожных карт
│  │  ├─ milestone.py         # Схемы этапов
│  │  ├─ stats.py             # Схема ответа статистики
│  │  └─ __init__.py
│  ├─ api/
│  │  ├─ deps.py              # Зависимости (current_user, current_active_user)
│  │  ├─ utils.py             # Вспомогательные функции (теги)
│  │  ├─ routes/
│  │  │  ├─ auth.py           # /auth/register, /auth/token
│  │  │  ├─ roadmaps.py       # /roadmaps, экспорт, фильтры
│  │  │  ├─ milestones.py     # /milestones
│  │  │  ├─ stats.py          # /stats
│  │  │  └─ __init__.py       # api_router
│  │  └─ __init__.py
│  └─ __init__.py
├─ tests/
│  ├─ conftest.py             # Настройка тестовой БД, клиента, фикстуры
│  ├─ test_auth.py            # Тесты регистрации и логина
│  ├─ test_roadmaps.py        # Тесты CRUD roadmaps
│  ├─ test_milestones.py      # Тесты CRUD milestones и валидации
│  ├─ test_stats.py           # Тесты статистики
│  ├─ test_validation.py      # Тесты валидации и owner-only доступа
│  └─ __init__.py             # (опционально)
├─ requirements.txt
└─ .gitignore
```

---

## Установка и запуск

### 1. Клонирование репозитория

```bash
git clone <URL_РЕПОЗИТОРИЯ> product_roadmap_app
cd product_roadmap_app
```

### 2. Виртуальное окружение

Создаём и активируем `.venv`:

```bash
python3 -m venv .venv
source .venv/bin/activate      # Linux/macOS
# или
.\.venv\Scripts\Activate.ps1   # Windows PowerShell
```

Проверь, что используется именно этот Python:

```bash
which python        # должен указывать на .../product_roadmap_app/.venv/bin/python
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

Содержимое `requirements.txt` (ориентировочно):

```text
fastapi==0.103.2
uvicorn[standard]==0.22.0
SQLAlchemy==1.4.52
python-jose[cryptography]==3.3.0
passlib==1.7.4
pydantic==1.10.13
email-validator==2.1.1
pytest==7.4.4
requests==2.32.3
```

### 4. Настройка окружения

По умолчанию используется SQLite:

```bash
export DATABASE_URL="sqlite:///./app.db"
```

Для PostgreSQL, пример:

```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/roadmaps"
```

(Схему нужно создать отдельно, миграции тут не используются, используется `Base.metadata.create_all`.)

### 5. Запуск приложения

```bash
uvicorn app.main:app --reload
```

Приложение будет доступно по адресу:

- Swagger UI: http://127.0.0.1:8000/docs
- OpenAPI JSON: http://127.0.0.1:8000/openapi.json

---

## Аутентификация

Используется OAuth2 Password Flow с JWT.

### Регистрация

```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "full_name": "User Name",
  "password": "strongpassword"
}
```

Ответ:

```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "User Name",
  "is_active": true,
  "created_at": "2025-12-07T10:00:00.000000"
}
```

### Получение токена

```http
POST /auth/token
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=strongpassword
```

Ответ:

```json
{
  "access_token": "<JWT>",
  "token_type": "bearer"
}
```

Дальше нужно передавать заголовок:

```http
Authorization: Bearer <JWT>
```

---

## Основные эндпоинты

Все защищённые эндпоинты требуют `Authorization: Bearer <JWT>`.

### Roadmaps

- `GET /roadmaps/`
  - Параметры:
    - `q` — поиск по `title` (ILIKE)
    - `tag` — фильтр по одному тегу
    - `is_archived` — фильтр по архивности
- `POST /roadmaps/`
- `GET /roadmaps/{roadmap_id}`
- `PUT /roadmaps/{roadmap_id}`
- `DELETE /roadmaps/{roadmap_id}`
- `GET /roadmaps/{roadmap_id}/export?format=json|csv`
  - Экспорт roadmap + milestones в JSON или CSV.

Теги хранятся в БД как строка `"tag1,tag2"`, но на уровне API — как список:

```json
{
  "title": "Backend Roadmap",
  "description": "API service",
  "tags": ["python", "fastapi"]
}
```

### Milestones

- `GET /milestones/`
  - Параметры:
    - `status` — фильтр по статусу (`planned`, `in_progress`, `done`, `cancelled`)
    - `due_before` — дедлайн раньше или равен дате
    - `due_after` — дедлайн позже или равен дате
    - `roadmap_id` — фильтр по конкретному roadmap
- `POST /milestones/`
- `GET /milestones/{milestone_id}`
- `PUT /milestones/{milestone_id}`
- `DELETE /milestones/{milestone_id}`

Особенности:

- `due_at` не должен быть в прошлом (проверяется при создании и обновлении через API).
- `due_at` не может быть раньше `created_at` соответствующего roadmap.
- Статусы — `MilestoneStatus` (enum).

### Статистика

- `GET /stats/`

Ответ:

```json
{
  "total_roadmaps": 3,
  "total_milestones": 12,
  "milestones_by_status": {
    "planned": 4,
    "in_progress": 5,
    "done": 3,
    "cancelled": 0
  },
  "overdue_milestones": 1,
  "upcoming_milestones_7d": 2
}
```

- `overdue_milestones` — milestones с `due_at < today` и `status != done`.
- `upcoming_milestones_7d` — milestones c `today <= due_at <= today + 7` и статусами `planned | in_progress`.

---

## Тестирование

Тесты написаны на Pytest и используют отдельную SQLite‑базу `test.db`, которая пересоздаётся **для каждого теста**.

### Запуск тестов

```bash
cd ~/product_roadmap_app
source .venv/bin/activate
python -m pytest -q
```

Структура тестов:

- `tests/conftest.py`
  - Настраивает `engine`, `TestingSessionLocal`, создаёт таблицы
  - Переопределяет зависимость `get_db` в приложении
  - Фикстуры:
    - `app` — инстанс FastAPI с тестовой БД
    - `client` — `TestClient`
    - `db_session` — SQLAlchemy Session
    - `test_user` — пользователь `test@example.com`
    - `auth_headers` — заголовки с JWT для `test_user`
- `test_auth.py`
  - Регистрация
  - Логин и получение JWT
- `test_roadmaps.py`
  - Создание и чтение roadmap
  - Фильтрация по тэгам
- `test_milestones.py`
  - Создание milestone
  - Валидация `due_at` через API (нельзя прошлую дату)
- `test_stats.py`
  - Пустая статистика
  - Статистика с данными:
    - один overdue milestone добавляется напрямую в БД
    - один upcoming создаётся через API
- `test_validation.py`
  - Проверка owner-only доступа (чужой пользователь не видит чужой roadmap)
  - Ещё один тест на валидацию даты

---

## Заметки по безопасности и валидации

- **AuthN/AuthZ**
  - Все маршруты `/roadmaps`, `/milestones`, `/stats` требуют авторизации.
  - Доступ к чужим ресурсам даёт `404`, чтобы сложнее было перебирать ID.
- **Хранение паролей**
  - Используется `pbkdf2_sha256` через Passlib.
- **Валидация дат**
  - `due_at` не может быть в прошлом при создании/обновлении через API.
  - `due_at` не может быть раньше даты создания `Roadmap` (business-валидация).
- **Теги и фильтры**
  - Теги нормализуются (lowercase, trim, уникальность, сортировка).
  - Фильтрация по тэгу — простая по подстроке (LIKE/ILIKE); для прод‑решения можно вынести в отдельную таблицу.

---

## TODO / возможные улучшения

- Вынести инициализацию БД в Alembic‑миграции.
- Добавить refresh-токены и logout.
- Расширить модель тегов до отдельной таблицы (`Tag`, `roadmap_tags`).
- Покрыть тестами экспорт `/roadmaps/{id}/export`.
- Добавить Dockerfile и docker-compose (API + Postgres).

```
