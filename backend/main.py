"""
Главный файл приложения FastAPI
"""
from fastapi import FastAPI, HTTPException
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
    description="REST API для мобильного приложения обмена книгами",
    version="1.0.0",
    lifespan=lifespan
)

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
    """Корневой endpoint"""
    return {
        "message": "Library Exchange API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Проверка здоровья приложения"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
