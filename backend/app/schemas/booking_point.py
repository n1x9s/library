"""
Схемы для пунктов выдачи
"""
from typing import Optional, List
from pydantic import BaseModel, validator, Field
from uuid import UUID


class BookingPointBase(BaseModel):
    """Базовая схема пункта выдачи"""
    name: str
    address: str
    coordinates: Optional[str] = None  # "lat,lng" format
    working_hours: str
    phone: Optional[str] = None

    @validator('name')
    def validate_name(cls, v):
        if len(v.strip()) < 1:
            raise ValueError('Название пункта выдачи не может быть пустым')
        return v.strip()

    @validator('address')
    def validate_address(cls, v):
        if len(v.strip()) < 1:
            raise ValueError('Адрес не может быть пустым')
        return v.strip()

    @validator('coordinates')
    def validate_coordinates(cls, v):
        if v is not None:
            try:
                lat, lng = v.split(',')
                lat = float(lat.strip())
                lng = float(lng.strip())
                if not (-90 <= lat <= 90):
                    raise ValueError('Широта должна быть между -90 и 90')
                if not (-180 <= lng <= 180):
                    raise ValueError('Долгота должна быть между -180 и 180')
            except (ValueError, IndexError):
                raise ValueError('Координаты должны быть в формате "широта,долгота"')
        return v

    @validator('phone')
    def validate_phone(cls, v):
        if v is not None:
            phone_digits = ''.join(filter(str.isdigit, v))
            if len(phone_digits) < 10:
                raise ValueError('Некорректный номер телефона')
        return v


class BookingPointResponse(BookingPointBase):
    """Схема ответа с данными пункта выдачи"""
    id: str = Field(..., description="ID пункта выдачи")
    is_active: bool

    @validator('id', pre=True)
    def convert_uuid_to_str(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return v

    class Config:
        from_attributes = True


class BookingPointListResponse(BaseModel):
    """Схема ответа со списком пунктов выдачи"""
    booking_points: List[BookingPointResponse]
    total: int
