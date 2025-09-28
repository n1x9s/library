"""
Обработка изображений
"""

import os
import uuid
from typing import Tuple
from PIL import Image
from fastapi import UploadFile, HTTPException, status
from app.core.config import settings


def validate_image(file: UploadFile) -> None:
    """Валидация загружаемого изображения"""
    # Проверка типа файла
    if file.content_type not in settings.allowed_image_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Неподдерживаемый тип файла. Разрешены: {', '.join(settings.allowed_image_types)}",
        )

    # Проверка размера файла
    file.file.seek(0, 2)  # Переход в конец файла
    file_size = file.file.tell()
    file.file.seek(0)  # Возврат в начало

    if file_size > settings.max_file_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Размер файла превышает {settings.max_file_size // 1024 // 1024}MB",
        )


def process_image(
    file: UploadFile, upload_dir: str, max_size: Tuple[int, int] = (800, 600)
) -> str:
    """
    Обработка и сохранение изображения

    Args:
        file: Загружаемый файл
        upload_dir: Директория для сохранения
        max_size: Максимальный размер (ширина, высота)

    Returns:
        str: Путь к сохраненному файлу
    """
    print(f"Начинаем обработку изображения: {file.filename}")
    print(f"Директория загрузки: {upload_dir}")
    
    # Создание директории если не существует
    os.makedirs(upload_dir, exist_ok=True)
    print(f"Директория создана/существует: {upload_dir}")

    # Генерация уникального имени файла
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in ["jpg", "jpeg", "png"]:
        file_extension = "jpg"

    filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(upload_dir, filename)
    print(f"Сгенерированное имя файла: {filename}")
    print(f"Полный путь: {file_path}")

    try:
        print("Открываем изображение...")
        # Открытие изображения
        with Image.open(file.file) as img:
            print(f"Исходный размер изображения: {img.size}")
            print(f"Режим изображения: {img.mode}")
            
            # Конвертация в RGB если необходимо
            if img.mode in ("RGBA", "LA", "P"):
                print("Конвертируем в RGB...")
                img = img.convert("RGB")

            # Изменение размера с сохранением пропорций
            print(f"Изменяем размер до: {max_size}")
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            print(f"Новый размер: {img.size}")

            # Сохранение изображения
            print("Сохраняем изображение...")
            img.save(file_path, "JPEG", quality=85, optimize=True)
            print(f"Изображение успешно сохранено: {file_path}")

        return file_path

    except Exception as e:
        print(f"Ошибка при обработке изображения: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка обработки изображения: {str(e)}",
        )


def delete_image(file_path: str) -> None:
    """Удаление изображения"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception:
        pass  # Игнорируем ошибки при удалении
