"""
API endpoints для аутентификации
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import os
from datetime import datetime
from app.core.database import get_db
from app.core.security import verify_token, get_user_id_from_token
from app.utils.image_processing import validate_image, process_image
from app.schemas.auth import Token, RefreshTokenRequest
from app.schemas.user import UserCreate, UserLogin, UserResponse, UserUpdate
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Аутентификация"])
security = HTTPBearer()


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """Получение ID текущего пользователя из токена"""
    token = credentials.credentials
    return get_user_id_from_token(token)


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Регистрация нового пользователя"""
    auth_service = AuthService(db)
    user = auth_service.register_user(user_data)
    return user


@router.post("/login", response_model=Token)
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """Вход в систему"""
    auth_service = AuthService(db)
    result = auth_service.login_user(login_data)
    return Token(
        access_token=result["access_token"],
        refresh_token=result["refresh_token"],
        token_type=result["token_type"],
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: RefreshTokenRequest, db: Session = Depends(get_db)
):
    """Обновление токена"""
    try:
        # Проверка refresh токена
        payload = verify_token(refresh_data.refresh_token, "refresh")
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Недействительный refresh токен",
            )

        # Проверка существования пользователя
        auth_service = AuthService(db)
        user = auth_service.get_user_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь не найден или деактивирован",
            )

        # Создание новых токенов
        from app.core.security import create_access_token, create_refresh_token

        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username}
        )
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        return Token(
            access_token=access_token, refresh_token=refresh_token, token_type="bearer"
        )

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный refresh токен",
        )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout():
    """Выход из системы (клиент должен удалить токены)"""
    return {"message": "Успешный выход из системы"}


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)
):
    """Получение профиля текущего пользователя"""
    auth_service = AuthService(db)
    user = auth_service.get_user_by_id(current_user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден"
        )

    return user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user_id: str = Depends(get_current_user_id),
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

    user = auth_service.update_user(current_user_id, update_data)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден"
        )

    return user


@router.post("/me/avatar", response_model=UserResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Загрузка аватара пользователя"""
    auth_service = AuthService(db)

    # Получаем пользователя
    user = auth_service.get_user_by_id(current_user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден"
        )

    # Валидируем загружаемый файл
    validate_image(file)

    # Создаем директорию для аватаров
    avatars_dir = os.path.join("static", "uploads", "avatars")
    os.makedirs(avatars_dir, exist_ok=True)

    # Обрабатываем и сохраняем изображение
    try:
        file_path = process_image(file, avatars_dir, max_size=(400, 400))

        # Удаляем старый аватар если есть
        if user.avatar_url:
            old_avatar_path = user.avatar_url.replace("/static/", "static/")
            if os.path.exists(old_avatar_path):
                os.remove(old_avatar_path)

        # Обновляем URL аватара в базе данных
        avatar_url = f"/static/uploads/avatars/{os.path.basename(file_path)}"
        user.avatar_url = avatar_url
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)

        return UserResponse.model_validate(user)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка при загрузке аватара: {str(e)}",
        )


@router.delete("/me/avatar", response_model=UserResponse)
async def delete_avatar(
    current_user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)
):
    """Удаление аватара пользователя"""
    auth_service = AuthService(db)

    # Получаем пользователя
    user = auth_service.get_user_by_id(current_user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден"
        )

    # Удаляем файл аватара если есть
    if user.avatar_url:
        avatar_path = user.avatar_url.replace("/static/", "static/")
        if os.path.exists(avatar_path):
            os.remove(avatar_path)

    # Очищаем URL аватара в базе данных
    user.avatar_url = None
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)

    return UserResponse.model_validate(user)
