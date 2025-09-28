"""
API endpoints для работы с книгами
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Request
from sqlalchemy.orm import Session
from typing import Optional
import os
from datetime import datetime
from app.core.database import get_db
from app.core.auth import get_current_user_id, get_current_user
from app.utils.image_processing import validate_image, process_image
from app.schemas.book import (
    BookCreate,
    BookUpdate,
    BookResponse,
    BookListResponse,
    BookSearchParams,
    BookSearchParams as SearchParams,
)
from app.services.book_service import BookService

router = APIRouter(prefix="/books", tags=["Книги"])


@router.get("/", response_model=BookListResponse)
async def get_books(
    search: Optional[str] = Query(
        None, description="Поиск по названию, автору или ISBN"
    ),
    genre: Optional[str] = Query(None, description="Фильтр по жанру"),
    author: Optional[str] = Query(None, description="Фильтр по автору"),
    owner_id: Optional[str] = Query(None, description="Фильтр по владельцу"),
    available_only: bool = Query(True, description="Показать только доступные книги"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    limit: int = Query(20, ge=1, le=100, description="Количество книг на странице"),
    db: Session = Depends(get_db),
):
    """Получение каталога книг с фильтрацией и поиском"""
    book_service = BookService(db)

    search_params = SearchParams(
        search=search,
        genre=genre,
        author=author,
        owner_id=owner_id,
        available_only=available_only,
        page=page,
        limit=limit,
    )

    books, total = book_service.get_books(search_params)

    # Преобразование в формат ответа
    book_responses = []
    for book in books:
        book_response = BookResponse.model_validate(book)
        book_responses.append(book_response)

    pages = (total + limit - 1) // limit

    return BookListResponse(
        books=book_responses, total=total, page=page, limit=limit, pages=pages
    )


@router.get("/{book_id}", response_model=BookResponse)
async def get_book(book_id: str, db: Session = Depends(get_db)):
    """Детальная информация о книге"""
    book_service = BookService(db)
    book = book_service.get_book_with_owner(book_id)

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Книга не найдена"
        )

    return book


@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(
    book_data: BookCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    """Добавление новой книги"""
    current_user_id = get_current_user_id(request)
    book_service = BookService(db)
    book = book_service.create_book(book_data, current_user_id)
    return book


@router.put("/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: str,
    book_data: BookUpdate,
    request: Request,
    db: Session = Depends(get_db),
):
    """Редактирование книги"""
    current_user_id = get_current_user_id(request)
    book_service = BookService(db)

    # Фильтруем None значения
    update_data = {k: v for k, v in book_data.dict().items() if v is not None}

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Нет данных для обновления"
        )

    book = book_service.update_book(book_id, BookUpdate(**update_data), current_user_id)

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Книга не найдена"
        )

    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Удаление книги"""
    current_user_id = get_current_user_id(request)
    book_service = BookService(db)
    success = book_service.delete_book(book_id, current_user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Книга не найдена"
        )


@router.post("/{book_id}/cover", response_model=BookResponse)
async def upload_book_cover(
    book_id: str,
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Загрузка обложки книги"""
    print(f"Загрузка обложки для книги {book_id}")
    print(f"Файл: {file.filename}, тип: {file.content_type}")
    
    current_user_id = get_current_user_id(request)
    print(f"Текущий пользователь: {current_user_id}")
    
    book_service = BookService(db)

    # Проверяем, что книга существует и принадлежит пользователю
    book = book_service.get_book_by_id(book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Книга не найдена"
        )

    if book.owner_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет прав для загрузки обложки этой книги",
        )

    # Валидируем загружаемый файл
    validate_image(file)

    # Создаем директорию для обложек книг
    book_covers_dir = os.path.join("static", "uploads", "book_covers")
    os.makedirs(book_covers_dir, exist_ok=True)

    # Обрабатываем и сохраняем изображение
    try:
        print(f"Обрабатываем изображение в директории: {book_covers_dir}")
        file_path = process_image(file, book_covers_dir, max_size=(800, 600))
        print(f"Изображение сохранено по пути: {file_path}")

        # Удаляем старую обложку если есть
        if book.cover_image_url:
            old_cover_path = book.cover_image_url.replace("/static/", "static/")
            if os.path.exists(old_cover_path):
                os.remove(old_cover_path)
                print(f"Удалена старая обложка: {old_cover_path}")

        # Обновляем URL обложки в базе данных
        cover_url = f"/static/uploads/book_covers/{os.path.basename(file_path)}"
        book.cover_image_url = cover_url
        book.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(book)
        
        print(f"Обложка обновлена в БД: {cover_url}")

        return BookResponse.model_validate(book)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка при загрузке обложки: {str(e)}",
        )


@router.delete("/{book_id}/cover", response_model=BookResponse)
async def delete_book_cover(
    book_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Удаление обложки книги"""
    current_user_id = get_current_user_id(request)
    book_service = BookService(db)

    # Проверяем, что книга существует и принадлежит пользователю
    book = book_service.get_book_by_id(book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Книга не найдена"
        )

    if book.owner_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет прав для удаления обложки этой книги",
        )

    # Удаляем файл обложки если есть
    if book.cover_image_url:
        cover_path = book.cover_image_url.replace("/static/", "static/")
        if os.path.exists(cover_path):
            os.remove(cover_path)

    # Очищаем URL обложки в базе данных
    book.cover_image_url = None
    book.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(book)

    return BookResponse.model_validate(book)


@router.get("/my/books", response_model=BookListResponse)
async def get_my_books(
    request: Request, db: Session = Depends(get_db)
):
    """Получение книг текущего пользователя"""
    current_user_id = get_current_user_id(request)
    book_service = BookService(db)
    books = book_service.get_user_books(current_user_id)

    # Преобразование в формат ответа
    book_responses = []
    for book in books:
        book_response = BookResponse.model_validate(book)
        book_responses.append(book_response)

    return BookListResponse(
        books=book_responses, total=len(books), page=1, limit=len(books), pages=1
    )
