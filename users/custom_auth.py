# custom_auth.py

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from .models import UserCode

UserModel = get_user_model()

class PhoneCodeAuthBackend(ModelBackend):
    """
    Пользовательский бэкенд аутентификации по номеру телефона и коду подтверждения.
    """

    class PhoneCodeAuthBackend(ModelBackend):
        def authenticate(self, request, **credentials):
            try:
                user = UserModel.objects.get(phone=credentials.get('phone'))
                return user
            except UserModel.DoesNotExist:
                return None

    # def authenticate(self, request, **credentials):
    #     """
    #     Аутентификация пользователя по номеру телефона и коду подтверждения.
    #
    #     Args:
    #         request: объект запроса Django.
    #         **credentials: переданные учетные данные (phone, verification_code).
    #
    #     Returns:
    #         User: объект пользователя, если аутентификация успешна, или None, если не удалось найти пользователя или проверить код подтверждения.
    #     """
    #     phone = credentials.get('phone')
    #     verification_code = credentials.get('verification_code')
    #
    #     if not phone or not verification_code:
    #         return None
    #
    #     try:
    #         # Поиск пользователя по номеру телефона
    #         user = UserModel.objects.get(phone=phone)
    #
    #         # Проверка кода подтверждения
    #         if self.validate_verification_code(user, verification_code):
    #             print(f"Успешная проверка кода подтверждения для пользователя {user.phone} код {verification_code}")
    #             return user
    #         else:
    #             print(f"Неверный код подтверждения для пользователя {user.phone} код {verification_code}")
    #             return None
    #     except UserModel.DoesNotExist:
    #         print(f"Пользователь с номером телефона {phone} не найден")
    #         return None

    # def validate_verification_code(self, user, verification_code):
    #     """
    #     Проверка кода подтверждения пользователя.
    #
    #     Args:
    #         user: объект пользователя.
    #         verification_code: код подтверждения для проверки.
    #
    #     Returns:
    #         bool: True, если код подтверждения действителен для пользователя, иначе False.
    #     """
    #     # Получение последнего сохраненного кода подтверждения для данного пользователя
    #     user_code = user.usercode_set.order_by('-created_at').first()
    #
    #     print(f"Ожидаемый код подтверждения: {user_code.sms_code}")
    #     print(f"Введенный код подтверждения: {verification_code}")
    #
    #     # Сравнение кода подтверждения
    #     if user_code and str(user_code.sms_code) == str(verification_code):
    #         print("Успешная проверка кода подтверждения")
    #         return True
    #     else:
    #         print("Неверный код подтверждения")
    #         return False