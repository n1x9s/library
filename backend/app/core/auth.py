"""
Аутентификация и авторизация
"""

from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.session import get_user_id_from_session
from app.models.user import User


def get_current_user_id(request: Request) -> str:
    """Получение ID текущего пользователя из сессии"""
    user_id = get_user_id_from_session(request)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Необходима аутентификация"
        )
    
    return user_id


def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    """Получение текущего пользователя из сессии"""
    user_id = get_current_user_id(request)
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Пользователь деактивирован"
        )
    
    return user