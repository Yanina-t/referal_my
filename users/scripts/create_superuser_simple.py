#python manage.py shell


from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.create(
    phone='1234567899',  # Укажите ваш номер телефона
    avatar=None,  # При желании можно указать путь к аватару пользователя
    is_active=True,
)
user.set_password('12345')  # Установим пароль
user.is_superuser = True  # Установим статус суперпользователя
user.is_staff = True  # Установим статус персонала (staff)
user.save()

exit()

from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.create(
    phone='1234567899',
    avatar=None,
    is_active=True,
)
user.set_password('12345')
user.is_superuser = True
user.is_staff = True
user.save()

exit()
