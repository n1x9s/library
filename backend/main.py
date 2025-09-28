"""
Главный файл приложения FastAPI
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from app.core.config import settings
from app.core.database import engine, Base
from app.api import auth, books, bookings, notifications


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Создание таблиц базы данных
    Base.metadata.create_all(bind=engine)

    # Создание директорий для загрузок
    os.makedirs(settings.upload_dir, exist_ok=True)
    os.makedirs(os.path.join(settings.upload_dir, "avatars"), exist_ok=True)
    os.makedirs(os.path.join(settings.upload_dir, "book_covers"), exist_ok=True)

    yield


# Создание приложения FastAPI
app = FastAPI(
    title="Library Exchange API",
    description="REST API для приложения обмена книгами",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Настройка OpenAPI схемы для сессионной аутентификации
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    from fastapi.openapi.utils import get_openapi
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Добавляем информацию о сессионной аутентификации
    openapi_schema["info"]["description"] = """
    REST API для приложения обмена книгами с сессионной аутентификацией.
    
    ## Аутентификация
    
    API использует сессионную аутентификацию через cookies:
    
    1. Войдите в систему через `POST /auth/login` с username и password
    2. После успешного входа будет установлен cookie `session_token`
    3. Все последующие запросы будут автоматически аутентифицированы
    4. Для выхода используйте `POST /auth/logout`
    
    ## Публичные эндпойнты
    
    - `GET /` - Информация об API
    - `GET /health` - Проверка здоровья
    - `POST /auth/register` - Регистрация
    - `POST /auth/login` - Вход в систему
    - `GET /books/` - Список книг
    - `GET /books/{book_id}` - Детали книги
    - `GET /bookings/booking-points` - Пункты выдачи
    
    ## Защищенные эндпойнты
    
    Все остальные эндпойнты требуют аутентификации через сессию.
    """
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение статических файлов
app.mount("/static", StaticFiles(directory="static"), name="static")

# Подключение роутеров
app.include_router(auth.router)
app.include_router(books.router)
app.include_router(bookings.router)
app.include_router(notifications.router)


@app.get("/")
async def root():
    """
    Корневой endpoint
    
    Информация о API и инструкции по сессионной аутентификации
    """
    return {
        "message": "Library Exchange API", 
        "version": "1.0.0", 
        "docs": "/docs",
        "authentication": {
            "type": "session_based",
            "login_endpoint": "/auth/login",
            "description": "Используйте /auth/login для входа в систему",
            "usage": "Отправьте POST запрос с username и password, получите cookie session_token",
            "note": "После входа все запросы автоматически аутентифицированы через cookie"
        },
        "endpoints": {
            "auth": "/auth/* - Аутентификация и управление пользователями",
            "books": "/books/* - Управление книгами",
            "bookings": "/bookings/* - Управление бронированиями",
            "notifications": "/notifications/* - Уведомления"
        },
        "public_endpoints": [
            "GET / - Информация об API",
            "GET /health - Проверка здоровья",
            "POST /auth/register - Регистрация",
            "POST /auth/login - Вход в систему",
            "GET /books/ - Список книг",
            "GET /books/{book_id} - Детали книги",
            "GET /bookings/booking-points - Пункты выдачи"
        ]
    }


@app.get("/health")
async def health_check():
    """Проверка здоровья приложения"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app", host=settings.host, port=settings.port, reload=settings.debug
    )
