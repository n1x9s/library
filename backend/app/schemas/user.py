"""
Схемы для пользователей
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, validator, Field
import re
from uuid import UUID


class UserBase(BaseModel):
    """Базовая схема пользователя"""

    email: EmailStr
    username: str
    full_name: str
    phone: Optional[str] = None

    @validator("username")
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError("Имя пользователя должно содержать минимум 3 символа")
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError(
                "Имя пользователя может содержать только буквы, цифры и подчеркивания"
            )
        return v

    @validator("phone")
    def validate_phone(cls, v):
        if v is not None:
            # Простая валидация номера телефона
            phone_digits = re.sub(r"\D", "", v)
            if len(phone_digits) < 10:
                raise ValueError("Некорректный номер телефона")
        return v


class UserCreate(UserBase):
    """Схема создания пользователя"""

    password: str

    @validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Пароль должен содержать минимум 8 символов")
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("Пароль должен содержать буквы")
        if not re.search(r"\d", v):
            raise ValueError("Пароль должен содержать цифры")
        return v


class UserUpdate(BaseModel):
    """Схема обновления пользователя"""

    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None

    @validator("username")
    def validate_username(cls, v):
        if v is not None:
            if len(v) < 3:
                raise ValueError("Имя пользователя должно содержать минимум 3 символа")
            if not re.match(r"^[a-zA-Z0-9_]+$", v):
                raise ValueError(
                    "Имя пользователя может содержать только буквы, цифры и подчеркивания"
                )
        return v

    @validator("phone")
    def validate_phone(cls, v):
        if v is not None:
            phone_digits = re.sub(r"\D", "", v)
            if len(phone_digits) < 10:
                raise ValueError("Некорректный номер телефона")
        return v


class UserLogin(BaseModel):
    """Схема входа пользователя"""

    email: EmailStr
    password: str


class UserResponse(UserBase):
    """Схема ответа с данными пользователя"""

    id: str = Field(..., description="ID пользователя")
    avatar_url: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    @validator("id", pre=True)
    def convert_uuid_to_str(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return v

    class Config:
        from_attributes = True


class UserStatistics(BaseModel):
    """Статистика пользователя"""

    books_count: int
    successful_bookings: int
    owner_rating: float
    total_usage_days: int
