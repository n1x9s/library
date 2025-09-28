"""
Сервис для работы с уведомлениями
"""

from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from app.models.notification import Notification, NotificationType
from app.models.user import User
from app.models.booking import Booking


class NotificationService:
    """Сервис для работы с уведомлениями"""

    def __init__(self, db: Session):
        self.db = db

    def create_notification(
        self,
        user_id: str,
        notification_type: NotificationType,
        title: str,
        message: str,
        booking_id: Optional[str] = None,
    ) -> Notification:
        """Создание уведомления"""
        notification = Notification(
            user_id=user_id,
            booking_id=booking_id,
            type=notification_type,
            title=title,
            message=message,
        )

        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)

        return notification

    def get_user_notifications(
        self, user_id: str, limit: int = 50, offset: int = 0
    ) -> List[Notification]:
        """Получение уведомлений пользователя"""
        return (
            self.db.query(Notification)
            .filter(Notification.user_id == user_id)
            .order_by(desc(Notification.created_at))
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_unread_count(self, user_id: str) -> int:
        """Получение количества непрочитанных уведомлений"""
        return (
            self.db.query(Notification)
            .filter(
                and_(Notification.user_id == user_id, Notification.is_read == False)
            )
            .count()
        )

    def mark_as_read(self, notification_id: str, user_id: str) -> bool:
        """Отметка уведомления как прочитанного"""
        notification = (
            self.db.query(Notification)
            .filter(
                and_(
                    Notification.id == notification_id, Notification.user_id == user_id
                )
            )
            .first()
        )

        if not notification:
            return False

        notification.is_read = True
        self.db.commit()

        return True

    def mark_all_as_read(self, user_id: str) -> int:
        """Отметка всех уведомлений как прочитанных"""
        updated_count = (
            self.db.query(Notification)
            .filter(
                and_(Notification.user_id == user_id, Notification.is_read == False)
            )
            .update({"is_read": True})
        )

        self.db.commit()
        return updated_count

    def create_booking_notification(self, booking: Booking) -> Notification:
        """Создание уведомления о новом бронировании для владельца книги"""
        book = (
            self.db.query(Booking.book)
            .join(Booking.book)
            .filter(Booking.id == booking.id)
            .first()
        )
        if not book:
            return None

        title = "Новое бронирование"
        message = f"Пользователь забронировал вашу книгу '{book.title}'"

        return self.create_notification(
            user_id=book.owner_id,
            notification_type=NotificationType.BOOKING_CREATED,
            title=title,
            message=message,
            booking_id=str(booking.id),
        )

    def create_return_reminder(self, booking: Booking) -> Notification:
        """Создание напоминания о возврате книги"""
        book = (
            self.db.query(Booking.book)
            .join(Booking.book)
            .filter(Booking.id == booking.id)
            .first()
        )
        if not book:
            return None

        title = "Напоминание о возврате"
        message = (
            f"Не забудьте вернуть книгу '{book.title}' до {booking.planned_return_date}"
        )

        return self.create_notification(
            user_id=booking.borrower_id,
            notification_type=NotificationType.RETURN_REMINDER,
            title=title,
            message=message,
            booking_id=str(booking.id),
        )

    def create_book_available_notification(
        self, book_id: str, user_id: str
    ) -> Notification:
        """Создание уведомления о доступности книги"""
        book = self.db.query(Book).filter(Book.id == book_id).first()
        if not book:
            return None

        title = "Книга доступна"
        message = f"Книга '{book.title}' снова доступна для бронирования"

        return self.create_notification(
            user_id=user_id,
            notification_type=NotificationType.BOOK_AVAILABLE,
            title=title,
            message=message,
        )

    def create_booking_cancelled_notification(self, booking: Booking) -> Notification:
        """Создание уведомления об отмене бронирования"""
        book = (
            self.db.query(Booking.book)
            .join(Booking.book)
            .filter(Booking.id == booking.id)
            .first()
        )
        if not book:
            return None

        # Уведомление для владельца книги
        title = "Бронирование отменено"
        message = f"Бронирование книги '{book.title}' было отменено"

        return self.create_notification(
            user_id=book.owner_id,
            notification_type=NotificationType.BOOKING_CANCELLED,
            title=title,
            message=message,
            booking_id=str(booking.id),
        )

    def cleanup_old_notifications(self, days: int = 30) -> int:
        """Очистка старых уведомлений"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        deleted_count = (
            self.db.query(Notification)
            .filter(
                and_(
                    Notification.created_at < cutoff_date, Notification.is_read == True
                )
            )
            .delete()
        )

        self.db.commit()
        return deleted_count
