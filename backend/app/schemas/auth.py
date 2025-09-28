"""
Схемы для аутентификации
"""

from typing import Optional
from pydantic import BaseModel, EmailStr


class UserLogin(BaseModel):
    """Схема входа пользователя"""
    
    username: str
    password: str


class Token(BaseModel):
    """Схема токена"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Данные из токена"""

    user_id: Optional[str] = None
    username: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    """Запрос на обновление токена"""

    refresh_token: str
