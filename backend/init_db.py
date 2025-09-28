"""
Скрипт для инициализации базы данных с тестовыми данными
"""

import asyncio
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.core.database import Base
from app.models import User, Book, BookingPoint, Booking, Notification
from app.core.security import get_password_hash
from app.models.book import BookCondition
from app.models.booking import BookingStatus
from datetime import datetime, date, timedelta

# Создание таблиц
Base.metadata.create_all(bind=engine)


def init_db():
    """Инициализация базы данных"""
    db = SessionLocal()

    try:
        # Проверяем, есть ли уже данные
        if db.query(User).first():
            print("База данных уже инициализирована")
            return

        # Создание тестовых пользователей
        users = [
            User(
                email="admin@library.com",
                username="admin",
                password_hash=get_password_hash("admin123"),
                full_name="Администратор",
                phone="+7-900-123-45-67",
                is_verified=True,
            ),
            User(
                email="user1@example.com",
                username="user1",
                password_hash=get_password_hash("user123"),
                full_name="Иван Петров",
                phone="+7-900-234-56-78",
            ),
            User(
                email="user2@example.com",
                username="user2",
                password_hash=get_password_hash("user123"),
                full_name="Мария Сидорова",
                phone="+7-900-345-67-89",
            ),
            User(
                email="user3@example.com",
                username="user3",
                password_hash=get_password_hash("user123"),
                full_name="Алексей Козлов",
                phone="+7-900-456-78-90",
            ),
        ]

        for user in users:
            db.add(user)
        db.commit()

        # Получаем созданных пользователей
        admin = db.query(User).filter(User.username == "admin").first()
        user1 = db.query(User).filter(User.username == "user1").first()
        user2 = db.query(User).filter(User.username == "user2").first()
        user3 = db.query(User).filter(User.username == "user3").first()

        # Создание пунктов выдачи
        booking_points = [
            BookingPoint(
                name="Центральная библиотека",
                address="ул. Ленина, 1, Москва",
                coordinates="55.7558,37.6176",
                working_hours="Пн-Пт: 9:00-21:00, Сб-Вс: 10:00-18:00",
                phone="+7-495-123-45-67",
            ),
            BookingPoint(
                name="Библиотека №2",
                address="пр. Мира, 15, Москва",
                coordinates="55.7619,37.6200",
                working_hours="Пн-Пт: 10:00-20:00, Сб: 10:00-16:00",
                phone="+7-495-234-56-78",
            ),
            BookingPoint(
                name="Книжный клуб",
                address="ул. Арбат, 25, Москва",
                coordinates="55.7522,37.5911",
                working_hours="Ежедневно: 11:00-23:00",
                phone="+7-495-345-67-89",
            ),
        ]

        for point in booking_points:
            db.add(point)
        db.commit()

        # Получаем созданные пункты выдачи
        point1 = (
            db.query(BookingPoint)
            .filter(BookingPoint.name == "Центральная библиотека")
            .first()
        )
        point2 = (
            db.query(BookingPoint).filter(BookingPoint.name == "Библиотека №2").first()
        )
        point3 = (
            db.query(BookingPoint).filter(BookingPoint.name == "Книжный клуб").first()
        )

        # Создание тестовых книг
        books = [
            Book(
                title="Война и мир",
                author="Лев Толстой",
                isbn="978-5-17-123456-7",
                description="Роман-эпопея Льва Толстого, описывающий русское общество в эпоху войн против Наполеона.",
                genre="Классическая литература",
                publication_year=1869,
                condition=BookCondition.GOOD,
                owner_id=user1.id,
                is_available=True,
            ),
            Book(
                title="Мастер и Маргарита",
                author="Михаил Булгаков",
                isbn="978-5-17-123457-4",
                description="Роман Михаила Булгакова, одно из самых загадочных произведений русской литературы.",
                genre="Классическая литература",
                publication_year=1967,
                condition=BookCondition.EXCELLENT,
                owner_id=user1.id,
                is_available=True,
            ),
            Book(
                title="1984",
                author="Джордж Оруэлл",
                isbn="978-5-17-123458-1",
                description="Антиутопический роман о тоталитарном обществе будущего.",
                genre="Научная фантастика",
                publication_year=1949,
                condition=BookCondition.GOOD,
                owner_id=user2.id,
                is_available=True,
            ),
            Book(
                title="Гарри Поттер и философский камень",
                author="Дж. К. Роулинг",
                isbn="978-5-17-123459-8",
                description="Первая книга серии о юном волшебнике Гарри Поттере.",
                genre="Фэнтези",
                publication_year=1997,
                condition=BookCondition.EXCELLENT,
                owner_id=user2.id,
                is_available=True,
            ),
            Book(
                title="Преступление и наказание",
                author="Фёдор Достоевский",
                isbn="978-5-17-123460-4",
                description="Роман о нравственных проблемах и психологии преступления.",
                genre="Классическая литература",
                publication_year=1866,
                condition=BookCondition.FAIR,
                owner_id=user3.id,
                is_available=True,
            ),
            Book(
                title="Собачье сердце",
                author="Михаил Булгаков",
                isbn="978-5-17-123461-1",
                description="Повесть о научном эксперименте, который пошёл не так.",
                genre="Классическая литература",
                publication_year=1925,
                condition=BookCondition.GOOD,
                owner_id=user3.id,
                is_available=True,
            ),
        ]

        for book in books:
            db.add(book)
        db.commit()

        # Создание тестовых бронирований
        bookings = [
            Booking(
                book_id=books[0].id,
                borrower_id=user2.id,
                booking_point_id=point1.id,
                status=BookingStatus.PENDING,
                planned_pickup_date=date.today() + timedelta(days=1),
                planned_return_date=date.today() + timedelta(days=15),
                notes="Буду забирать после работы",
            ),
            Booking(
                book_id=books[2].id,
                borrower_id=user3.id,
                booking_point_id=point2.id,
                status=BookingStatus.CONFIRMED,
                planned_pickup_date=date.today() + timedelta(days=2),
                planned_return_date=date.today() + timedelta(days=16),
                notes="Спасибо за книгу!",
            ),
        ]

        for booking in bookings:
            db.add(booking)
        db.commit()

        # Создание тестовых уведомлений
        notifications = [
            Notification(
                user_id=user1.id,
                booking_id=bookings[0].id,
                type="booking_created",
                title="Новое бронирование",
                message="Пользователь user2 забронировал вашу книгу 'Война и мир'",
            ),
            Notification(
                user_id=user2.id,
                booking_id=bookings[1].id,
                type="booking_created",
                title="Бронирование подтверждено",
                message="Ваше бронирование книги '1984' подтверждено владельцем",
            ),
        ]

        for notification in notifications:
            db.add(notification)
        db.commit()

        print("База данных успешно инициализирована с тестовыми данными")
        print("Созданы пользователи:")
        print("- admin@library.com / admin123 (администратор)")
        print("- user1@example.com / user123 (Иван Петров)")
        print("- user2@example.com / user123 (Мария Сидорова)")
        print("- user3@example.com / user123 (Алексей Козлов)")
        print(f"Создано {len(books)} книг")
        print(f"Создано {len(booking_points)} пунктов выдачи")
        print(f"Создано {len(bookings)} бронирований")
        print(f"Создано {len(notifications)} уведомлений")

    except Exception as e:
        print(f"Ошибка при инициализации базы данных: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
