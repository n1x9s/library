"""
Управление сессиями пользователей
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Request, Response
from sqlalchemy.orm import Session
from app.models.user import User

# В реальном приложении это должно храниться в Redis или базе данных
# Для простоты используем словарь в памяти
active_sessions = {}

SESSION_COOKIE_NAME = "session_token"
SESSION_EXPIRE_HOURS = 24 * 7  # 7 дней


def create_session_token(user_id: str) -> str:
    """Создает новый токен сессии для пользователя"""
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=SESSION_EXPIRE_HOURS)
    
    active_sessions[token] = {
        "user_id": user_id,
        "expires_at": expires_at,
        "created_at": datetime.utcnow()
    }
    
    return token


def get_user_id_from_session(request: Request) -> Optional[str]:
    """Получает ID пользователя из сессии"""
    session_token = request.cookies.get(SESSION_COOKIE_NAME)
    
    if not session_token:
        return None
    
    session_data = active_sessions.get(session_token)
    
    if not session_data:
        return None
    
    # Проверяем, не истекла ли сессия
    if datetime.utcnow() > session_data["expires_at"]:
        # Удаляем истекшую сессию
        active_sessions.pop(session_token, None)
        return None
    
    return session_data["user_id"]


def clear_session(request: Request, response: Response) -> None:
    """Очищает сессию пользователя"""
    session_token = request.cookies.get(SESSION_COOKIE_NAME)
    
    if session_token:
        # Удаляем сессию из памяти
        active_sessions.pop(session_token, None)
    
    # Удаляем cookie
    response.delete_cookie(SESSION_COOKIE_NAME)


def set_session_cookie(response: Response, session_token: str) -> None:
    """Устанавливает cookie с токеном сессии"""
    response.set_cookie(
        SESSION_COOKIE_NAME,
        session_token,
        max_age=SESSION_EXPIRE_HOURS * 3600,  # в секундах
        httponly=True,  # Защита от XSS
        secure=False,   # В продакшене должно быть True для HTTPS
        samesite="lax"  # Защита от CSRF
    )