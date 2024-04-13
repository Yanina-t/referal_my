# utils.py
from users.models import User, UserCode
from django.utils.crypto import get_random_string
from django.conf import settings
from django.core.cache import cache
import time
import random


def generate_invite_code():
    """Генерирует уникальный инвайт-код для пользователя."""
    # Генерируем случайный инвайт-код
    invite_code = get_random_string(length=6, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')

    return invite_code


def activate_invite_code(current_user, invite_code):
    """Активирует инвайт-код для пользователя, если он еще не использован."""
    # Найти пользователя, связанного с инвайт-кодом
    ref_user = User.objects.filter(invite_code=invite_code).first()

    if ref_user:
        # Проверить, что у текущего пользователя нет активированного инвайт-кода
        if not current_user.invite_code_used:
            # Присвоить текущему пользователю реферера
            current_user.ref_user = ref_user
            current_user.invite_code_used = True
            current_user.save()
            return True
        else:
            return False  # Уже активирован инвайт-код у текущего пользователя
    else:
        return False  # Инвайт-код не найден или уже использован


def send_verification_code(phone_number):
    """Отправляет код подтверждения на указанный номер телефона (имитация)."""
    # Генерируем случайный код подтверждения
    verification_code = f"{random.randint(1000, 9999)}"

    # Создаем уникальный ключ кэша для сохранения кода подтверждения
    cache_key = f"verification_code_{phone_number}"

    # Сохраняем пару phone_number и verification_code в кэше на некоторое время
    cache.set(cache_key, verification_code, timeout=settings.VERIFICATION_CODE_EXPIRATION_TIME)

    # Выводим сообщение о том, что SMS отправлено
    print(f"Отправлено SMS на номер {phone_number} с кодом: {verification_code}")

    # Имитируем задержку, как если бы SMS было бы отправлено в реальном времени
    time.sleep(2)  # Задержка на 2 секунды (для имитации отправки SMS)

    # Возвращаем сгенерированный код подтверждения
    return verification_code


def create_user_with_verification_code(phone_number):
    """Создает пользователя с уникальным инвайт-кодом и отправляет код подтверждения."""
    # Отправляем код подтверждения
    verification_code = send_verification_code(phone_number)

    # Создаем пользователя, если его еще нет
    user, created = User.objects.get_or_create(phone=phone_number, defaults={'invite_code': generate_invite_code()})

    # Создаем запись с кодом подтверждения для пользователя
    user_code = UserCode.objects.create(user=user, sms_code=verification_code)

    return user, user_code