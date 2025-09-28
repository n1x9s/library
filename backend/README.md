# Library Exchange Backend

REST API для приложения обмена книгами с сессионной аутентификацией.

## Особенности

- **Сессионная аутентификация** - вход через `/auth/login` с автоматической аутентификацией всех запросов
- **FastAPI** - современный веб-фреймворк для Python
- **SQLAlchemy** - ORM для работы с базой данных
- **PostgreSQL** - основная база данных
- **Alembic** - миграции базы данных
- **Celery** - асинхронные задачи
- **Redis** - кэширование и брокер сообщений

## Быстрый старт

1. Установите зависимости:
   ```bash
   uv sync
   ```

2. Настройте переменные окружения в `.env`:
   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/library_db
   SECRET_KEY=your-secret-key-here
   ```

3. Запустите миграции:
   ```bash
   alembic upgrade head
   ```

4. Запустите сервер:
   ```bash
   uv run main.py
   ```

5. Откройте документацию: http://localhost:8000/docs

## Аутентификация

API использует сессионную аутентификацию:

1. Войдите через `POST /auth/login` с username и password
2. После входа cookie `session_token` автоматически устанавливается
3. Все последующие запросы автоматически аутентифицированы
4. Для выхода используйте `POST /auth/logout`

## Тестирование

```bash
# Базовые тесты
python test_session_auth.py

# Тест с учетными данными
python test_session_auth.py username password
```

## Документация

- [Сессионная аутентификация](SESSION_AUTH_README.md)
- [Аутентификация через JWT](AUTH_README.md) (устарело)
