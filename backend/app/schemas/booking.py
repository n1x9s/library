"""
Схемы для бронирования
"""

from typing import Optional, List
from datetime import datetime, date
from pydantic import BaseModel, validator, Field
from uuid import UUID
from app.models.booking import BookingStatus


class BookingBase(BaseModel):
    """Базовая схема бронирования"""

    book_id: str
    booking_point_id: str
    planned_pickup_date: date
    planned_return_date: date
    notes: Optional[str] = None

    @validator("planned_pickup_date")
    def validate_pickup_date(cls, v):
        if v < date.today():
            raise ValueError("Дата получения не может быть в прошлом")
        return v

    @validator("planned_return_date")
    def validate_return_date(cls, v, values):
        if "planned_pickup_date" in values and v <= values["planned_pickup_date"]:
            raise ValueError("Дата возврата должна быть позже даты получения")
        return v


class BookingCreate(BookingBase):
    """Схема создания бронирования"""

    pass


class BookingUpdate(BaseModel):
    """Схема обновления бронирования"""

    status: Optional[BookingStatus] = None
    planned_pickup_date: Optional[date] = None
    planned_return_date: Optional[date] = None
    notes: Optional[str] = None

    @validator("planned_pickup_date")
    def validate_pickup_date(cls, v):
        if v is not None and v < date.today():
            raise ValueError("Дата получения не может быть в прошлом")
        return v

    @validator("planned_return_date")
    def validate_return_date(cls, v, values):
        if (
            v is not None
            and "planned_pickup_date" in values
            and values["planned_pickup_date"] is not None
        ):
            if v <= values["planned_pickup_date"]:
                raise ValueError("Дата возврата должна быть позже даты получения")
        return v


class BookingResponse(BookingBase):
    """Схема ответа с данными бронирования"""

    id: str = Field(..., description="ID бронирования")
    borrower_id: str = Field(..., description="ID заемщика")
    status: BookingStatus
    booking_date: datetime
    actual_pickup_date: Optional[datetime] = None
    actual_return_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    book: Optional[dict] = None
    borrower: Optional[dict] = None
    booking_point: Optional[dict] = None

    @validator("id", "borrower_id", "book_id", "booking_point_id", pre=True)
    def convert_uuid_to_str(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return v

    @validator("book", "borrower", "booking_point", pre=True)
    def convert_objects_to_dict(cls, v):
        if v is not None and hasattr(v, "id"):
            # Если это объект модели, преобразуем в словарь
            if hasattr(v, "username"):  # User объект
                return {
                    "id": str(v.id),
                    "username": v.username,
                    "full_name": v.full_name,
                }
            elif hasattr(v, "title"):  # Book объект
                return {"id": str(v.id), "title": v.title, "author": v.author}
            elif hasattr(v, "name"):  # BookingPoint объект
                return {"id": str(v.id), "name": v.name, "address": v.address}
        return v

    class Config:
        from_attributes = True


class BookingListResponse(BaseModel):
    """Схема ответа со списком бронирований"""

    bookings: List[BookingResponse]
    total: int
    page: int
    limit: int
    pages: int


class BookingSearchParams(BaseModel):
    """Параметры поиска бронирований"""

    status: Optional[BookingStatus] = None
    as_borrower: bool = False
    as_owner: bool = False
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


class BookingStatusUpdate(BaseModel):
    """Схема обновления статуса бронирования"""

    status: BookingStatus
    notes: Optional[str] = None
