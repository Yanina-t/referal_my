#models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

NULLABLE = {'blank': True, 'null': True}


# Create your models here.
# noinspection PyArgumentList
class User(AbstractUser):  # models.Model
    """Модель пользователя с дополнительными полями."""
    username = None
    phone = models.CharField(max_length=12, unique=True, verbose_name='Номер телефона')
    invite_code = models.CharField(max_length=6, unique=True, verbose_name='Инвайт-код пользователя')
    activated_invite_code = models.CharField(max_length=6, **NULLABLE,
                                             verbose_name='Чужой инвайт-код')
    ref_user = models.ForeignKey('self', **NULLABLE, on_delete=models.CASCADE, verbose_name='Реферал')
    first_name = models.CharField(max_length=50, **NULLABLE, verbose_name='Имя пользователя')
    last_name = models.CharField(max_length=100, **NULLABLE, verbose_name='Фамилия пользователя')
    email = models.EmailField(unique=True, **NULLABLE, verbose_name='Email')
    avatar = models.ImageField(upload_to='avatars/', **NULLABLE)
    is_authenticated = models.BooleanField(default=False, verbose_name='Авторизован')

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.phone


# Users.objects.filter(ref_user=requrest.user)
# Users.objects.filter(invite_code=...)

class UserCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sms_code = models.PositiveSmallIntegerField(verbose_name='SMS-код')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания sms-кода')

    def __str__(self):
        return f"{self.user.phone} - {self.sms_code}"
