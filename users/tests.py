from django.test import TestCase

# Create your tests here.
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status

from users.custom_auth import PhoneCodeAuthBackend
from users.models import User
from users.utils import generate_invite_code


class PhoneAuthAPIViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_phone_auth_form_display(self):
        """Тестирование отображения формы ввода номера телефона."""
        response = self.client.get(reverse('users:phone_auth'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'users/enter_phone.html')

    def test_phone_auth_success(self):
        """Тестирование успешной авторизации по номеру телефона."""
        data = {'phone': '1234567890'}
        response = self.client.post(reverse('users:phone_auth'), data)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:verify_code'))

    def test_phone_auth_failure(self):
        """Тестирование неудачной авторизации по номеру телефона."""
        response = self.client.post(reverse('users:phone_auth'), {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Добавьте дополнительные проверки сообщений об ошибках в ответе


class UtilsTestCase(TestCase):

    def test_generate_invite_code_unique(self):
        # Генерируем уникальный инвайт-код
        invite_code = generate_invite_code()

        # Проверяем, что инвайт-код уникален
        self.assertTrue(User.objects.filter(invite_code=invite_code).count() == 0)

        # Создаем пользователя с этим инвайт-кодом
        user = User.objects.create(phone='9876543210', invite_code=invite_code)

        # Проверяем, что пользователь успешно создан
        self.assertIsNotNone(user)
        self.assertEqual(user.phone, '9876543210')
        self.assertEqual(user.invite_code, invite_code)


class AuthBackendTestCase(TestCase):
    def setUp(self):
        self.backend = PhoneCodeAuthBackend()
        self.user = User.objects.create(phone='1234567890')

    def test_authenticate_with_valid_phone(self):
        """Тестирование аутентификации по номеру телефона."""
        user = self.backend.authenticate(None, phone='1234567890')
        self.assertEqual(user, self.user)  # Ожидаем успешную аутентификацию

    def test_authenticate_with_invalid_phone(self):
        """Тестирование аутентификации с неверным номером телефона."""
        user = self.backend.authenticate(None, phone='9999999999')
        self.assertIsNone(user)  # Ожидаем неудачную аутентификацию

