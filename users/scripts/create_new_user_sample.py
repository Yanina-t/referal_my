# python manage.py shell

# Импорт модели User
# Импорт функции create_new_user
# Вызов функции для создания нового пользователя
# Проверка результата

from users.models import User
from users.scripts.create_new_user import create_new_user

phone_number = "986667721012"
invite_code = "AB66EF"
new_user = create_new_user(phone_number, invite_code)

if new_user:
    print("Пользователь успешно создан!")
else:
    print("Не удалось создать пользователя.")
