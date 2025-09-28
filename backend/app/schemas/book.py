"""
Схемы для книг
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, validator, Field
import re
from uuid import UUID
from app.models.book import BookCondition


class BookBase(BaseModel):
    """Базовая схема книги"""

    title: str
    author: str
    description: Optional[str] = None
    genre: Optional[str] = None
    publication_year: Optional[int] = None
    condition: BookCondition = BookCondition.GOOD

    @validator("title")
    def validate_title(cls, v):
        if len(v.strip()) < 1:
            raise ValueError("Название книги не может быть пустым")
        return v.strip()

    @validator("author")
    def validate_author(cls, v):
        if len(v.strip()) < 1:
            raise ValueError("Автор не может быть пустым")
        return v.strip()

    @validator("publication_year")
    def validate_publication_year(cls, v):
        if v is not None:
            current_year = datetime.now().year
            if v < 1000 or v > current_year + 1:
                raise ValueError(
                    f"Год публикации должен быть между 1000 и {current_year + 1}"
                )
        return v


class BookCreate(BookBase):
    """Схема создания книги"""

    pass


class BookUpdate(BaseModel):
    """Схема обновления книги"""

    title: Optional[str] = None
    author: Optional[str] = None
    description: Optional[str] = None
    genre: Optional[str] = None
    publication_year: Optional[int] = None
    condition: Optional[BookCondition] = None

    @validator("title")
    def validate_title(cls, v):
        if v is not None:
            if len(v.strip()) < 1:
                raise ValueError("Название книги не может быть пустым")
            return v.strip()
        return v

    @validator("author")
    def validate_author(cls, v):
        if v is not None:
            if len(v.strip()) < 1:
                raise ValueError("Автор не может быть пустым")
            return v.strip()
        return v

    @validator("publication_year")
    def validate_publication_year(cls, v):
        if v is not None:
            current_year = datetime.now().year
            if v < 1000 or v > current_year + 1:
                raise ValueError(
                    f"Год публикации должен быть между 1000 и {current_year + 1}"
                )
        return v


class BookResponse(BookBase):
    """Схема ответа с данными книги"""

    id: str = Field(..., description="ID книги")
    cover_image_url: Optional[str] = None
    owner_id: str = Field(..., description="ID владельца")
    is_available: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    owner: Optional[dict] = None
    bookings: Optional[List[dict]] = None

    @validator("id", "owner_id", pre=True)
    def convert_uuid_to_str(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return v

    @validator("owner", pre=True)
    def convert_owner_to_dict(cls, v):
        if v is not None and hasattr(v, "id"):
            # Если это объект User, преобразуем в словарь
            return {"id": str(v.id), "username": v.username, "full_name": v.full_name}
        return v

    @validator("bookings", pre=True)
    def convert_bookings_to_dict(cls, v):
        if v is not None:
            # Если это список объектов Booking, преобразуем в список словарей
            return [
                {
                    "id": str(booking.id),
                    "borrower_id": str(booking.borrower_id),
                    "status": booking.status.value if hasattr(booking.status, 'value') else booking.status,
                    "booking_date": booking.booking_date.isoformat() if booking.booking_date else None,
                    "planned_pickup_date": booking.planned_pickup_date.isoformat() if booking.planned_pickup_date else None,
                    "planned_return_date": booking.planned_return_date.isoformat() if booking.planned_return_date else None,
                    "actual_pickup_date": booking.actual_pickup_date.isoformat() if booking.actual_pickup_date else None,
                    "actual_return_date": booking.actual_return_date.isoformat() if booking.actual_return_date else None,
                }
                for booking in v
            ]
        return v

    class Config:
        from_attributes = True


class BookListResponse(BaseModel):
    """Схема ответа со списком книг"""

    books: List[BookResponse]
    total: int
    page: int
    limit: int
    pages: int


class BookSearchParams(BaseModel):
    """Параметры поиска книг"""

    search: Optional[str] = None
    genre: Optional[str] = None
    author: Optional[str] = None
    owner_id: Optional[str] = None
    available_only: bool = True
    page: int = 1
    limit: int = 20

    @validator("page")
    def validate_page(cls, v):
        if v < 1:
            raise ValueError("Страница должна быть больше 0")
        return v

    @validator("limit")
    def validate_limit(cls, v):
        if v < 1 or v > 100:
            raise ValueError("Лимит должен быть от 1 до 100")
        return v
