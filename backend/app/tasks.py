"""
Фоновые задачи Celery
"""

from datetime import datetime, timedelta
from celery import current_task
from sqlalchemy.orm import sessionmaker
from app.core.database import engine
from app.core.config import settings
from app.models.booking import Booking, BookingStatus
from app.models.notification import Notification
from app.services.notification_service import NotificationService
from app.celery_app import celery_app

# Создание сессии для задач
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Получение сессии базы данных для задач"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@celery_app.task
def send_return_reminders():
    """Отправка напоминаний о возврате книг"""
    db = next(get_db())
    notification_service = NotificationService(db)

    try:
        # Находим бронирования, которые нужно вернуть завтра
        tomorrow = datetime.now().date() + timedelta(days=1)

        bookings = (
            db.query(Booking)
            .filter(
                Booking.status == BookingStatus.TAKEN,
                Booking.planned_return_date == tomorrow,
            )
            .all()
        )

        reminders_sent = 0
        for booking in bookings:
            try:
                notification_service.create_return_reminder(booking)
                reminders_sent += 1
            except Exception as e:
                print(f"Ошибка отправки напоминания для бронирования {booking.id}: {e}")

        return f"Отправлено напоминаний: {reminders_sent}"

    except Exception as e:
        print(f"Ошибка в задаче send_return_reminders: {e}")
        raise
    finally:
        db.close()


@celery_app.task
def cleanup_old_notifications():
    """Очистка старых уведомлений"""
    db = next(get_db())
    notification_service = NotificationService(db)

    try:
        deleted_count = notification_service.cleanup_old_notifications(days=30)
        return f"Удалено старых уведомлений: {deleted_count}"

    except Exception as e:
        print(f"Ошибка в задаче cleanup_old_notifications: {e}")
        raise
    finally:
        db.close()


@celery_app.task
def send_booking_notification(booking_id: str):
    """Отправка уведомления о новом бронировании"""
    db = next(get_db())
    notification_service = NotificationService(db)

    try:
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if booking:
            notification_service.create_booking_notification(booking)
            return f"Уведомление отправлено для бронирования {booking_id}"
        else:
            return f"Бронирование {booking_id} не найдено"

    except Exception as e:
        print(f"Ошибка в задаче send_booking_notification: {e}")
        raise
    finally:
        db.close()


@celery_app.task
def send_booking_cancelled_notification(booking_id: str):
    """Отправка уведомления об отмене бронирования"""
    db = next(get_db())
    notification_service = NotificationService(db)

    try:
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if booking:
            notification_service.create_booking_cancelled_notification(booking)
            return f"Уведомление об отмене отправлено для бронирования {booking_id}"
        else:
            return f"Бронирование {booking_id} не найдено"

    except Exception as e:
        print(f"Ошибка в задаче send_booking_cancelled_notification: {e}")
        raise
    finally:
        db.close()


@celery_app.task
def send_book_available_notification(book_id: str, user_id: str):
    """Отправка уведомления о доступности книги"""
    db = next(get_db())
    notification_service = NotificationService(db)

    try:
        notification_service.create_book_available_notification(book_id, user_id)
        return f"Уведомление о доступности отправлено для книги {book_id}"

    except Exception as e:
        print(f"Ошибка в задаче send_book_available_notification: {e}")
        raise
    finally:
        db.close()
