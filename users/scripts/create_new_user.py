# create_new_user.py
from django.db import IntegrityError
from django.utils import timezone

from users.models import User


def create_new_user(phone_number, invite_code):
    try:
        # Создаем нового пользователя
        user = User.objects.create(
            phone=phone_number,
            invite_code=invite_code,
            is_active=True,
            date_joined=timezone.now()
        )
        return user
    except IntegrityError as e:
        # Обработка ошибки создания пользователя
        print(f"Ошибка при создании пользователя: {e}")
        return None

# Пример вызова функции create_new_user с конкретными параметрами
new_user = create_new_user("987677721012", "AB55EF")

if new_user:
    print("Пользователь успешно создан!")
else:
    print("Не удалось создать пользователя.")
