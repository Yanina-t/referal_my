from users.models import User, UserCode
from django.utils.crypto import get_random_string
from django.conf import settings
from django.core.cache import cache
import time
import random

def generate_invite_code():
    """
    Генерация уникального инвайт-кода пользователя.
    """
    # Генерируем случайный инвайт-код
    invite_code = get_random_string(length=6, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')

    return invite_code

def send_verification_code(phone_number):
    """
    Отправка кода подтверждения на указанный номер телефона (имитация).
    """
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
    """
    Создание пользователя с уникальным инвайт-кодом и отправка кода подтверждения.
    """
    # Отправляем код подтверждения
    verification_code = send_verification_code(phone_number)

    # Создаем пользователя, если его еще нет
    user, created = User.objects.get_or_create(phone=phone_number, defaults={'invite_code_u': generate_invite_code()})

    # Создаем запись с кодом подтверждения для пользователя
    user_code = UserCode.objects.create(user=user, sms_code=verification_code)

    return user, user_code
