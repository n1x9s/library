"""
API endpoints для аутентификации
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request, Response
from sqlalchemy.orm import Session
import os
from datetime import datetime
from app.core.database import get_db
from app.core.session import create_session_token, clear_session
from app.core.auth import get_current_user_id, get_current_user
from app.utils.image_processing import validate_image, process_image
from app.schemas.user import UserCreate, UserLogin, UserResponse, UserUpdate
from app.services.auth_service import AuthService
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Аутентификация"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Регистрация нового пользователя"""
    auth_service = AuthService(db)
    user = auth_service.register_user(user_data)
    return user


@router.post("/login", response_model=UserResponse)
async def login(
    login_data: UserLogin, 
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Вход в систему
    
    Создает сессию пользователя и устанавливает cookie.
    После успешного входа вы автоматически получите доступ ко всем защищенным эндпойнтам.
    """
    auth_service = AuthService(db)
    user = auth_service.authenticate_user(login_data.username, login_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Пользователь деактивирован"
        )
    
    # Создаем токен сессии
    session_token = create_session_token(str(user.id))
    
    # Устанавливаем cookie с токеном сессии
    response.set_cookie(
        key="session_token",
        value=session_token,
        max_age=86400,  # 24 часа
        httponly=True,  # Защита от XSS
        secure=False,   # В продакшене должно быть True для HTTPS
        samesite="lax"
    )
    
    return UserResponse.model_validate(user)




@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(request: Request, response: Response):
    """
    Выход из системы
    
    Очищает сессию пользователя и удаляет cookie.
    """
    # Очищаем сессию
    clear_session(request)
    
    # Удаляем cookie
    response.delete_cookie(
        key="session_token",
        httponly=True,
        samesite="lax"
    )
    
    return {"message": "Успешный выход из системы"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Получение профиля текущего пользователя
    
    Проверяет валидность сессии и возвращает информацию о пользователе.
    Используйте этот эндпойнт для проверки аутентификации.
    """
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Обновление профиля текущего пользователя"""
    auth_service = AuthService(db)

    # Фильтруем None значения
    update_data = {k: v for k, v in user_data.dict().items() if v is not None}

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Нет данных для обновления"
        )

    user = auth_service.update_user(str(current_user.id), update_data)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден"
        )

    return user


@router.post("/me/avatar", response_model=UserResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Загрузка аватара пользователя"""
    # Валидируем загружаемый файл
    validate_image(file)

    # Создаем директорию для аватаров
    avatars_dir = os.path.join("static", "uploads", "avatars")
    os.makedirs(avatars_dir, exist_ok=True)

    # Обрабатываем и сохраняем изображение
    try:
        file_path = process_image(file, avatars_dir, max_size=(400, 400))

        # Удаляем старый аватар если есть
        if current_user.avatar_url:
            old_avatar_path = current_user.avatar_url.replace("/static/", "static/")
            if os.path.exists(old_avatar_path):
                os.remove(old_avatar_path)

        # Обновляем URL аватара в базе данных
        avatar_url = f"/static/uploads/avatars/{os.path.basename(file_path)}"
        current_user.avatar_url = avatar_url
        current_user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(current_user)

        return UserResponse.model_validate(current_user)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка при загрузке аватара: {str(e)}",
        )


@router.delete("/me/avatar", response_model=UserResponse)
async def delete_avatar(
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Удаление аватара пользователя"""
    # Удаляем файл аватара если есть
    if current_user.avatar_url:
        avatar_path = current_user.avatar_url.replace("/static/", "static/")
        if os.path.exists(avatar_path):
            os.remove(avatar_path)

    # Очищаем URL аватара в базе данных
    current_user.avatar_url = None
    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)

    return UserResponse.model_validate(current_user)
