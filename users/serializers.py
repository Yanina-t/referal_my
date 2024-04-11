# # serializers.py
# from django.contrib.auth.hashers import make_password
# from rest_framework import serializers
# from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
# from users.models import User
#
#
# class UserSerializer(serializers.ModelSerializer):
#     """
#     Хэширование пароля
#     """
#     password = serializers.CharField(write_only=True)
#
#     def create(self, validated_data):
#         user = User.objects.create_user(**validated_data)
#         return user
#
#     class Meta:
#         model = User
#         fields = ['id', 'phone', 'password']
#
#
# class PhoneAuthSerializer(serializers.Serializer):
#     phone_number = serializers.CharField(max_length=12)
#
#     def validate_phone_number(self, value):
#         # Проверка формата номера телефона (пример: должен быть только из цифр 381601234567)
#         if not value.isdigit():
#             raise serializers.ValidationError("Номер телефона должен содержать только цифры. 381601234567")
#
#         # Проверка уникальности номера телефона в базе данных
#         if User.objects.filter(phone=value).exists():
#             raise serializers.ValidationError(f"Пользователь с таким номером телефона ({value}) уже зарегистрирован.")
#
#         return value
#
#
# class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
#     """
#     Сериализатор для получения пары токенов (обновляемого токена и доступа) при входе пользователя в систему.
#     """
#
#     @classmethod
#     def get_token(cls, user):
#         """
#         Получение токена для пользователя.
#         """
#         token = super().get_token(user)
#         # Добавление дополнительной информации в токен, если необходимо
#         return token
from rest_framework import serializers
from users.models import User

class PhoneAuthSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=12)

    def validate_phone_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Номер телефона должен содержать только цифры.")
        return value

class VerifyCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=12)
    verification_code = serializers.CharField(max_length=4)

    def validate_phone_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Номер телефона должен содержать только цифры.")
        return value
