"""
Сервис для работы с книгами
"""
from typing import List, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from fastapi import HTTPException, status
from app.models.book import Book
from app.models.user import User
from app.schemas.book import BookCreate, BookUpdate, BookSearchParams


class BookService:
    """Сервис для работы с книгами"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_book(self, book_data: BookCreate, owner_id: str) -> Book:
        """Создание новой книги"""
        # Проверка существования владельца
        owner = self.db.query(User).filter(User.id == owner_id).first()
        if not owner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        
        # Создание книги
        db_book = Book(
            title=book_data.title,
            author=book_data.author,
            description=book_data.description,
            genre=book_data.genre,
            publication_year=book_data.publication_year,
            condition=book_data.condition,
            owner_id=owner_id
        )
        
        self.db.add(db_book)
        self.db.commit()
        self.db.refresh(db_book)
        
        return db_book
    
    def get_book_by_id(self, book_id: str) -> Optional[Book]:
        """Получение книги по ID"""
        return self.db.query(Book).options(joinedload(Book.owner)).filter(Book.id == book_id).first()
    
    def get_books(self, search_params: BookSearchParams) -> Tuple[List[Book], int]:
        """Получение списка книг с фильтрацией"""
        query = self.db.query(Book).options(joinedload(Book.owner)).filter(Book.is_active == True)
        
        # Фильтр по доступности
        if search_params.available_only:
            query = query.filter(Book.is_available == True)
        
        # Поиск по тексту
        if search_params.search:
            search_term = f"%{search_params.search}%"
            query = query.filter(
                or_(
                    Book.title.ilike(search_term),
                    Book.author.ilike(search_term)
                )
            )
        
        # Фильтр по жанру
        if search_params.genre:
            query = query.filter(Book.genre.ilike(f"%{search_params.genre}%"))
        
        # Фильтр по автору
        if search_params.author:
            query = query.filter(Book.author.ilike(f"%{search_params.author}%"))
        
        # Фильтр по владельцу
        if search_params.owner_id:
            query = query.filter(Book.owner_id == search_params.owner_id)
        
        # Подсчет общего количества
        total = query.count()
        
        # Пагинация
        offset = (search_params.page - 1) * search_params.limit
        books = query.offset(offset).limit(search_params.limit).all()
        
        return books, total
    
    def get_user_books(self, user_id: str) -> List[Book]:
        """Получение книг пользователя"""
        return self.db.query(Book).options(joinedload(Book.owner)).filter(
            and_(Book.owner_id == user_id, Book.is_active == True)
        ).all()
    
    def update_book(self, book_id: str, book_data: BookUpdate, user_id: str) -> Optional[Book]:
        """Обновление книги"""
        book = self.get_book_by_id(book_id)
        if not book:
            return None
        
        # Проверка прав владельца
        if book.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нет прав для редактирования этой книги"
            )
        
        # Валидация ISBN если указан
        if book_data.isbn and not validate_isbn(book_data.isbn):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Некорректный ISBN"
            )
        
        # Обновление полей
        for field, value in book_data.dict(exclude_unset=True).items():
            if hasattr(book, field) and value is not None:
                setattr(book, field, value)
        
        book.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(book)
        
        return book
    
    def delete_book(self, book_id: str, user_id: str) -> bool:
        """Удаление книги"""
        book = self.get_book_by_id(book_id)
        if not book:
            return False
        
        # Проверка прав владельца
        if book.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нет прав для удаления этой книги"
            )
        
        # Проверка активных бронирований
        active_bookings = self.db.query(Book).join(Book.bookings).filter(
            and_(
                Book.id == book_id,
                Book.bookings.any(status.in_(["pending", "confirmed", "taken"]))
            )
        ).first()
        
        if active_bookings:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нельзя удалить книгу с активными бронированиями"
            )
        
        # Мягкое удаление
        book.is_active = False
        book.is_available = False
        book.updated_at = datetime.utcnow()
        self.db.commit()
        
        return True
    
    def update_book_availability(self, book_id: str, is_available: bool) -> bool:
        """Обновление доступности книги"""
        book = self.get_book_by_id(book_id)
        if not book:
            return False
        
        book.is_available = is_available
        book.updated_at = datetime.utcnow()
        self.db.commit()
        
        return True
    
    def get_book_with_owner(self, book_id: str) -> Optional[Book]:
        """Получение книги с информацией о владельце"""
        return self.db.query(Book).join(User).filter(Book.id == book_id).first()
