"""
Сервис аутентификации
"""
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token


class AuthService:
    """Сервис для работы с аутентификацией"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def register_user(self, user_data: UserCreate) -> User:
        """Регистрация нового пользователя"""
        # Проверка существования пользователя с таким email
        existing_user = self.db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже существует"
            )
        
        # Проверка существования пользователя с таким username
        existing_username = self.db.query(User).filter(User.username == user_data.username).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким именем уже существует"
            )
        
        # Создание нового пользователя
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            password_hash=hashed_password,
            full_name=user_data.full_name,
            phone=user_data.phone
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Аутентификация пользователя"""
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        return user
    
    def login_user(self, login_data: UserLogin) -> dict:
        """Вход пользователя в систему"""
        user = self.authenticate_user(login_data.email, login_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Аккаунт деактивирован"
            )
        
        # Создание токенов
        access_token = create_access_token(data={"sub": str(user.id), "username": user.username})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user
        }
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Получение пользователя по ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def update_user(self, user_id: str, update_data: dict) -> Optional[User]:
        """Обновление данных пользователя"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        # Проверка уникальности email если он изменяется
        if "email" in update_data and update_data["email"] != user.email:
            existing_user = self.db.query(User).filter(User.email == update_data["email"]).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Пользователь с таким email уже существует"
                )
        
        # Проверка уникальности username если он изменяется
        if "username" in update_data and update_data["username"] != user.username:
            existing_username = self.db.query(User).filter(User.username == update_data["username"]).first()
            if existing_username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Пользователь с таким именем уже существует"
                )
        
        # Обновление полей
        for field, value in update_data.items():
            if hasattr(user, field) and value is not None:
                setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """Смена пароля пользователя"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        # Проверка старого пароля
        if not verify_password(old_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный текущий пароль"
            )
        
        # Установка нового пароля
        user.password_hash = get_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        self.db.commit()
        
        return True
