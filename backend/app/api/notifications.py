"""
API endpoints для работы с уведомлениями
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_user_id_from_token
from app.schemas.notification import (
    NotificationResponse,
    NotificationListResponse,
    NotificationMarkRead,
)
from app.services.notification_service import NotificationService
from app.models.notification import Notification

router = APIRouter(prefix="/notifications", tags=["Уведомления"])
security = HTTPBearer()


def get_current_user_id(credentials=Depends(security)) -> str:
    """Получение ID текущего пользователя из токена"""
    token = credentials.credentials
    return get_user_id_from_token(token)


@router.get("/", response_model=NotificationListResponse)
async def get_notifications(
    limit: int = 50,
    offset: int = 0,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Получение уведомлений пользователя"""
    notification_service = NotificationService(db)

    notifications = notification_service.get_user_notifications(
        current_user_id, limit, offset
    )
    unread_count = notification_service.get_unread_count(current_user_id)

    # Преобразование в формат ответа
    notification_responses = []
    for notification in notifications:
        notification_dict = {
            "id": str(notification.id),
            "user_id": str(notification.user_id),
            "booking_id": (
                str(notification.booking_id) if notification.booking_id else None
            ),
            "type": notification.type,
            "title": notification.title,
            "message": notification.message,
            "is_read": notification.is_read,
            "created_at": notification.created_at,
        }
        notification_responses.append(notification_dict)

    return NotificationListResponse(
        notifications=notification_responses,
        total=len(notifications),
        unread_count=unread_count,
    )


@router.put("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: str,
    read_data: NotificationMarkRead,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Отметка уведомления как прочитанного"""
    notification_service = NotificationService(db)
    success = notification_service.mark_as_read(notification_id, current_user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Уведомление не найдено"
        )

    # Получаем обновленное уведомление
    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id, Notification.user_id == current_user_id
        )
        .first()
    )

    return notification


@router.put("/read-all", status_code=status.HTTP_200_OK)
async def mark_all_notifications_read(
    current_user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)
):
    """Отметка всех уведомлений как прочитанных"""
    notification_service = NotificationService(db)
    updated_count = notification_service.mark_all_as_read(current_user_id)

    return {"message": f"Отмечено как прочитанных: {updated_count} уведомлений"}
