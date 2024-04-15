# serializers.py
from rest_framework import serializers
from users.models import User


class UserProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для профиля пользователя."""
    class Meta:
        model = User
        fields = ['id', 'phone', 'first_name', 'last_name', 'email', 'avatar']


class ReferralSerializer(serializers.ModelSerializer):
    """Сериализатор для данных о рефералах."""
    class Meta:
        model = User
        fields = ['id', 'phone', 'first_name', 'last_name']

    def to_representation(self, instance):
        """Переопределение метода to_representation для представления данных о реферале."""
        data = super().to_representation(instance)
        data['name'] = f"{instance.first_name} {instance.last_name}"
        return data


class PhoneAuthSerializer(serializers.Serializer):
    """Сериализатор для валидации номера телефона."""
    phone = serializers.CharField(max_length=12)

    def validate_phone_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Номер телефона должен содержать только цифры.")
        return value


class VerifyCodeSerializer(serializers.Serializer):
    """Сериализатор для валидации номера телефона и кода подтверждения."""
    phone_number = serializers.CharField(max_length=12)
    verification_code = serializers.CharField(max_length=4)

    def validate_phone_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Номер телефона должен содержать только цифры.")
        return value


class ProfileEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'avatar']
