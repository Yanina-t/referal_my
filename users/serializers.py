# serializers.py
from rest_framework import serializers
from users.models import User


class UserProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для профиля пользователя."""
    invite_code = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'phone', 'invite_code']

    def update(self, instance, validated_data):
        """Обновляет профиль пользователя при активации инвайт-кода."""
        invite_code = validated_data.get('invite_code')
        if invite_code and not instance.ref_user:
            ref_user = User.objects.filter(invite_code=invite_code).first()
            if ref_user:
                instance.ref_user = ref_user
                instance.save()
        return instance


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


