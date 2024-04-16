# custom_auth.py

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

UserModel = get_user_model()


class PhoneCodeAuthBackend(ModelBackend):
    """
    Пользовательский бэкенд аутентификации по номеру телефона и коду подтверждения.
    """
    def authenticate(self, request, **credentials):
        try:
            user = UserModel.objects.get(phone=credentials.get('phone'))
            return user
        except UserModel.DoesNotExist:
            return None
