"""
Сервис для работы с бронированиями
"""

from typing import List, Optional, Tuple
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from fastapi import HTTPException, status
from app.models.booking import Booking, BookingStatus
from app.models.book import Book
from app.models.user import User
from app.models.booking_point import BookingPoint
from app.schemas.booking import BookingCreate, BookingUpdate, BookingSearchParams


class BookingService:
    """Сервис для работы с бронированиями"""

    def __init__(self, db: Session):
        self.db = db

    def create_booking(self, booking_data: BookingCreate, borrower_id: str) -> Booking:
        """Создание нового бронирования"""
        # Проверка существования книги
        book = self.db.query(Book).filter(Book.id == booking_data.book_id).first()
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Книга не найдена"
            )

        # Проверка доступности книги
        if not book.is_available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Книга недоступна для бронирования",
            )

        # Проверка, что пользователь не бронирует свою книгу
        if book.owner_id == borrower_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нельзя бронировать собственную книгу",
            )

        # Проверка существования пункта выдачи
        booking_point = (
            self.db.query(BookingPoint)
            .filter(BookingPoint.id == booking_data.booking_point_id)
            .first()
        )
        if not booking_point:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Пункт выдачи не найден"
            )

        # Проверка существования заемщика
        borrower = self.db.query(User).filter(User.id == borrower_id).first()
        if not borrower:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден"
            )

        # Проверка активных бронирований этой книги
        existing_booking = (
            self.db.query(Booking)
            .filter(
                and_(
                    Booking.book_id == booking_data.book_id,
                    Booking.status.in_(
                        [
                            BookingStatus.PENDING,
                            BookingStatus.CONFIRMED,
                            BookingStatus.TAKEN,
                        ]
                    ),
                )
            )
            .first()
        )

        if existing_booking:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Книга уже забронирована",
            )

        # Создание бронирования
        db_booking = Booking(
            book_id=booking_data.book_id,
            borrower_id=borrower_id,
            booking_point_id=booking_data.booking_point_id,
            planned_pickup_date=booking_data.planned_pickup_date,
            planned_return_date=booking_data.planned_return_date,
            notes=booking_data.notes,
        )

        self.db.add(db_booking)

        # Обновление доступности книги
        book.is_available = False
        book.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(db_booking)

        return db_booking

    def get_booking_by_id(self, booking_id: str) -> Optional[Booking]:
        """Получение бронирования по ID"""
        return (
            self.db.query(Booking)
            .options(
                joinedload(Booking.book),
                joinedload(Booking.borrower),
                joinedload(Booking.booking_point),
            )
            .filter(Booking.id == booking_id)
            .first()
        )

    def get_user_bookings(
        self, user_id: str, search_params: BookingSearchParams
    ) -> Tuple[List[Booking], int]:
        """Получение бронирований пользователя"""
        query = self.db.query(Booking).options(
            joinedload(Booking.book),
            joinedload(Booking.borrower),
            joinedload(Booking.booking_point),
        )

        # Фильтр по пользователю
        if search_params.as_borrower and search_params.as_owner:
            # Показать все бронирования где пользователь заемщик или владелец книги
            query = query.join(Book).filter(
                or_(Booking.borrower_id == user_id, Book.owner_id == user_id)
            )
        elif search_params.as_borrower:
            query = query.filter(Booking.borrower_id == user_id)
        elif search_params.as_owner:
            query = query.join(Book).filter(Book.owner_id == user_id)
        else:
            # По умолчанию показываем как заемщика
            query = query.filter(Booking.borrower_id == user_id)

        # Фильтр по статусу
        if search_params.status:
            query = query.filter(Booking.status == search_params.status)

        # Подсчет общего количества
        total = query.count()

        # Пагинация
        offset = (search_params.page - 1) * search_params.limit
        bookings = query.offset(offset).limit(search_params.limit).all()

        return bookings, total

    def update_booking_status(
        self, booking_id: str, new_status: BookingStatus, user_id: str
    ) -> Optional[Booking]:
        """Обновление статуса бронирования"""
        booking = self.get_booking_by_id(booking_id)
        if not booking:
            return None

        # Получение книги для проверки прав
        book = self.db.query(Book).filter(Book.id == booking.book_id).first()
        if not book:
            return None

        # Проверка прав (владелец книги или заемщик)
        if book.owner_id != user_id and booking.borrower_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нет прав для изменения статуса этого бронирования",
            )

        # Логика изменения статуса
        old_status = booking.status

        # Владелец может подтвердить или отменить
        if book.owner_id == user_id:
            if (
                new_status == BookingStatus.CONFIRMED
                and old_status == BookingStatus.PENDING
            ):
                booking.status = new_status
            elif new_status == BookingStatus.CANCELLED and old_status in [
                BookingStatus.PENDING,
                BookingStatus.CONFIRMED,
            ]:
                booking.status = new_status
                # Возвращаем доступность книги
                book.is_available = True
                book.updated_at = datetime.utcnow()
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Недопустимое изменение статуса",
                )

        # Заемщик может отменить только pending бронирование
        elif booking.borrower_id == user_id:
            if (
                new_status == BookingStatus.CANCELLED
                and old_status == BookingStatus.PENDING
            ):
                booking.status = new_status
                # Возвращаем доступность книги
                book.is_available = True
                book.updated_at = datetime.utcnow()
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Недопустимое изменение статуса",
                )

        booking.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(booking)

        return booking

    def confirm_pickup(self, booking_id: str, user_id: str) -> Optional[Booking]:
        """Подтверждение получения книги"""
        booking = self.get_booking_by_id(booking_id)
        if not booking:
            return None

        # Только заемщик может подтвердить получение
        if booking.borrower_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Только заемщик может подтвердить получение книги",
            )

        if booking.status != BookingStatus.CONFIRMED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Бронирование должно быть подтверждено владельцем",
            )

        booking.status = BookingStatus.TAKEN
        booking.actual_pickup_date = datetime.utcnow()
        booking.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(booking)

        return booking

    def confirm_return(self, booking_id: str, user_id: str) -> Optional[Booking]:
        """Подтверждение возврата книги"""
        booking = self.get_booking_by_id(booking_id)
        if not booking:
            return None

        # Только заемщик может подтвердить возврат
        if booking.borrower_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Только заемщик может подтвердить возврат книги",
            )

        if booking.status != BookingStatus.TAKEN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Книга должна быть получена перед возвратом",
            )

        booking.status = BookingStatus.RETURNED
        booking.actual_return_date = datetime.utcnow()
        booking.updated_at = datetime.utcnow()

        # Возвращаем доступность книги
        book = self.db.query(Book).filter(Book.id == booking.book_id).first()
        if book:
            book.is_available = True
            book.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(booking)

        return booking

    def cancel_booking(self, booking_id: str, user_id: str) -> bool:
        """Отмена бронирования"""
        booking = self.get_booking_by_id(booking_id)
        if not booking:
            return False

        # Проверка прав
        book = self.db.query(Book).filter(Book.id == booking.book_id).first()
        if not book:
            return False

        if book.owner_id != user_id and booking.borrower_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нет прав для отмены этого бронирования",
            )

        # Можно отменить только pending или confirmed бронирования
        if booking.status not in [BookingStatus.PENDING, BookingStatus.CONFIRMED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Невозможно отменить бронирование в текущем статусе",
            )

        booking.status = BookingStatus.CANCELLED
        booking.updated_at = datetime.utcnow()

        # Возвращаем доступность книги
        book.is_available = True
        book.updated_at = datetime.utcnow()

        self.db.commit()

        return True
