"""
Схемы для уведомлений
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator
from uuid import UUID
from app.models.notification import NotificationType


class NotificationResponse(BaseModel):
    """Схема ответа с данными уведомления"""

    id: str = Field(..., description="ID уведомления")
    user_id: str = Field(..., description="ID пользователя")
    booking_id: Optional[str] = Field(None, description="ID бронирования")
    type: NotificationType
    title: str
    message: str
    is_read: bool
    created_at: datetime

    @validator("id", "user_id", "booking_id", pre=True)
    def convert_uuid_to_str(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return v

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """Схема ответа со списком уведомлений"""

    notifications: List[NotificationResponse]
    total: int
    unread_count: int


class NotificationMarkRead(BaseModel):
    """Схема отметки уведомления как прочитанного"""

    is_read: bool = True
