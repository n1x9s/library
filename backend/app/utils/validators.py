"""
Валидаторы
"""
import re
from typing import Optional


def validate_isbn(isbn: str) -> bool:
    """
    Валидация ISBN
    
    Args:
        isbn: ISBN для проверки
    
    Returns:
        bool: True если ISBN валиден
    """
    if not isbn:
        return True  # ISBN не обязателен
    
    # Удаляем все нецифровые символы кроме X
    isbn_clean = re.sub(r'[^0-9X]', '', isbn.upper())
    
    if len(isbn_clean) == 10:
        return _validate_isbn10(isbn_clean)
    elif len(isbn_clean) == 13:
        return _validate_isbn13(isbn_clean)
    
    return False


def _validate_isbn10(isbn: str) -> bool:
    """Валидация ISBN-10"""
    if len(isbn) != 10:
        return False
    
    # Проверка контрольной суммы
    total = 0
    for i, digit in enumerate(isbn):
        if digit == 'X':
            if i != 9:  # X может быть только в последней позиции
                return False
            total += 10 * (10 - i)
        else:
            total += int(digit) * (10 - i)
    
    return total % 11 == 0


def _validate_isbn13(isbn: str) -> bool:
    """Валидация ISBN-13"""
    if len(isbn) != 13:
        return False
    
    # Проверка контрольной суммы
    total = 0
    for i, digit in enumerate(isbn):
        if i % 2 == 0:
            total += int(digit)
        else:
            total += int(digit) * 3
    
    return total % 10 == 0


def validate_phone(phone: str) -> bool:
    """
    Валидация номера телефона
    
    Args:
        phone: Номер телефона для проверки
    
    Returns:
        bool: True если номер валиден
    """
    if not phone:
        return True  # Телефон не обязателен
    
    # Удаляем все нецифровые символы
    phone_digits = re.sub(r'\D', '', phone)
    
    # Проверяем длину (минимум 10 цифр)
    return len(phone_digits) >= 10


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Проверка силы пароля
    
    Args:
        password: Пароль для проверки
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Пароль должен содержать минимум 8 символов"
    
    if not re.search(r'[A-Za-z]', password):
        return False, "Пароль должен содержать буквы"
    
    if not re.search(r'\d', password):
        return False, "Пароль должен содержать цифры"
    
    return True, ""


def validate_coordinates(coordinates: str) -> bool:
    """
    Валидация координат в формате "широта,долгота"
    
    Args:
        coordinates: Координаты для проверки
    
    Returns:
        bool: True если координаты валидны
    """
    if not coordinates:
        return True  # Координаты не обязательны
    
    try:
        lat, lng = coordinates.split(',')
        lat = float(lat.strip())
        lng = float(lng.strip())
        
        return -90 <= lat <= 90 and -180 <= lng <= 180
    except (ValueError, IndexError):
        return False
