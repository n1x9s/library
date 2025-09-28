"""
API endpoints для работы с бронированиями
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.auth import get_current_user_id
from app.schemas.booking import (
    BookingCreate,
    BookingUpdate,
    BookingResponse,
    BookingListResponse,
    BookingSearchParams,
    BookingStatusUpdate,
)
from app.schemas.booking_point import BookingPointResponse
from app.services.booking_service import BookingService
from app.models.booking_point import BookingPoint

router = APIRouter(prefix="/bookings", tags=["Бронирования"])


@router.get("/booking-points", response_model=list[BookingPointResponse])
async def get_booking_points(db: Session = Depends(get_db)):
    """Получение списка пунктов выдачи"""
    booking_points = db.query(BookingPoint).filter(BookingPoint.is_active == True).all()
    return booking_points


@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_data: BookingCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    """Создание бронирования"""
    current_user_id = get_current_user_id(request)
    booking_service = BookingService(db)
    booking = booking_service.create_booking(booking_data, current_user_id)
    return booking


@router.get("/", response_model=BookingListResponse)
async def get_bookings(
    status: Optional[str] = Query(None, description="Фильтр по статусу"),
    as_borrower: bool = Query(False, description="Показать как заемщик"),
    as_owner: bool = Query(False, description="Показать как владелец"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    limit: int = Query(20, ge=1, le=100, description="Количество на странице"),
    request: Request = None,
    db: Session = Depends(get_db),
):
    """Получение бронирований пользователя"""
    current_user_id = get_current_user_id(request)
    booking_service = BookingService(db)

    search_params = BookingSearchParams(
        status=status,
        as_borrower=as_borrower,
        as_owner=as_owner,
        page=page,
        limit=limit,
    )

    bookings, total = booking_service.get_user_bookings(current_user_id, search_params)

    # Преобразование в формат ответа
    booking_responses = []
    for booking in bookings:
        booking_response = BookingResponse.model_validate(booking)
        booking_responses.append(booking_response)

    pages = (total + limit - 1) // limit

    return BookingListResponse(
        bookings=booking_responses, total=total, page=page, limit=limit, pages=pages
    )


@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Детальная информация о бронировании"""
    current_user_id = get_current_user_id(request)
    booking_service = BookingService(db)
    booking = booking_service.get_booking_by_id(booking_id)

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Бронирование не найдено"
        )

    # Проверка прав доступа
    book = booking.book
    if not book or (
        book.owner_id != current_user_id and booking.borrower_id != current_user_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет прав для просмотра этого бронирования",
        )

    return booking


@router.put("/{booking_id}/status", response_model=BookingResponse)
async def update_booking_status(
    booking_id: str,
    status_data: BookingStatusUpdate,
    request: Request,
    db: Session = Depends(get_db),
):
    """Изменение статуса бронирования"""
    current_user_id = get_current_user_id(request)
    booking_service = BookingService(db)
    booking = booking_service.update_booking_status(
        booking_id, status_data.status, current_user_id
    )

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Бронирование не найдено"
        )

    return booking


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_booking(
    booking_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Отмена бронирования"""
    current_user_id = get_current_user_id(request)
    booking_service = BookingService(db)
    success = booking_service.cancel_booking(booking_id, current_user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Бронирование не найдено"
        )


@router.post("/{booking_id}/confirm-pickup", response_model=BookingResponse)
async def confirm_pickup(
    booking_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Подтверждение получения книги"""
    current_user_id = get_current_user_id(request)
    booking_service = BookingService(db)
    booking = booking_service.confirm_pickup(booking_id, current_user_id)

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Бронирование не найдено"
        )

    return booking


@router.post("/{booking_id}/confirm-return", response_model=BookingResponse)
async def confirm_return(
    booking_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Подтверждение возврата книги"""
    current_user_id = get_current_user_id(request)
    booking_service = BookingService(db)
    booking = booking_service.confirm_return(booking_id, current_user_id)

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Бронирование не найдено"
        )

    return booking


@router.post("/{booking_id}/return", status_code=status.HTTP_200_OK)
async def return_booking(
    booking_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Возврат книги"""
    current_user_id = get_current_user_id(request)
    booking_service = BookingService(db)
    
    success = booking_service.return_book(booking_id, current_user_id)
    
    if success:
        return {"message": "Книга успешно возвращена"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка при возврате книги"
        )
