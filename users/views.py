# views.py
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView
from rest_framework.generics import get_object_or_404, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from users.models import User, UserCode
from .serializers import PhoneAuthSerializer, UserProfileSerializer, VerifyCodeSerializer
from .utils import create_user_with_verification_code
from rest_framework import generics


class HomePageView(View):
    def get(self, request):
        return render(request, 'users/home.html')

class UserProfileAPIView(APIView):
    """Отображает профиль пользователя и позволяет активировать инвайт-код."""
    template_name = 'user_profile.html'

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super().get_context_data(**kwargs)
        context['user'] = user
        context['profile_form'] = UserProfileSerializer(instance=user)
        return context

    # queryset = User.objects.all()
    # serializer_class = UserProfileSerializer
    # permission_classes = [IsAuthenticated]
    # lookup_field = 'phone'  # Используем идентификатор пользователя (id) для поиска

    # def get_object(self):
    #     """
    #     Получить профиль текущего пользователя.
    #     """
    #     return self.request.user

    def post(self, request):
        """Активирует инвайт-код для текущего пользователя."""
        serializer = UserProfileSerializer(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserReferralsAPIView(generics.ListAPIView):
    """Отображает список пользователей, которые ввели инвайт-код текущего пользователя."""
    serializer_class = UserProfileSerializer
    queryset = User.objects.all()  # Можно настроить для вашей модели User

    def list(self, request, *args, **kwargs):
        # Получаем текущего пользователя
        user = self.request.user

        # Получаем список пользователей, которые использовали инвайт-код текущего пользователя
        referrals = user.referrals.all()  # Предположим, что у пользователя есть связь referrals

        # Можно использовать другую логику для получения списка пользователей по инвайтам
        # Например, если инвайт коды хранятся в другой модели

        serializer = self.get_serializer(referrals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PhoneAuthAPIView(APIView):
    """API-представление для авторизации по номеру телефона."""
    template_name = 'users/enter_phone.html'
    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        serializer = PhoneAuthSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        phone_number = serializer.validated_data['phone']

        # Сохраняем номер телефона в сессии для последующих запросов
        request.session['phone_number'] = phone_number


        try:
            # Создаем пользователя с уникальным инвайт-кодом и отправляем код подтверждения
            user, user_code = create_user_with_verification_code(phone_number)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Выводим SMS-код в консоль для проверки
        print(f'Отправлен SMS-код на номер {phone_number}: {user_code.sms_code}')



        # Устанавливаем сессию для пользователя
        login(request, user)

        # Перенаправляем пользователя на страницу ввода SMS-кода
        return redirect('users:verify_code')



        # return Response({'phone_number': phone_number, 'verification_code': user_code.sms_code, 'message': f'Код подтверждения отправлен на номер {phone_number}'}, status=status.HTTP_200_OK)


class VerifyCodeAPIView(APIView):
    """API-представление для проверки кода подтверждения."""
    def get(self, request):
        # Показать форму ввода кода подтверждения (это можно использовать, если GET запрос будет использоваться для отображения формы)
        return render(request, 'users/verify_code.html')

    def post(self, request):
        # Выводим содержимое запроса в консоль
        print(f"POST request data: {request.data}")
        serializer = VerifyCodeSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = request.session.get('phone_number')
            verification_code = serializer.validated_data.get('verification_code')

            # Далее ваша логика для проверки кода подтверждения
            print(f"Phone number: {phone_number}, Verification code: {verification_code}")

            if phone_number and verification_code:
                # Найдите пользователя по номеру телефона
                user = User.objects.filter(phone=phone_number).first()

                if not user:
                    return Response({'error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)

                # Найдите последний сохраненный код подтверждения для данного пользователя
                user_code = UserCode.objects.filter(user=user).order_by('-created_at').first()

                if not user_code:
                    return Response({'error': 'Код подтверждения не найден'}, status=status.HTTP_404_NOT_FOUND)

                # Сравните коды
                if str(user_code.sms_code) == str(verification_code):
                    # Удалите использованный код подтверждения
                    user_code.delete()

                    # Обновите статус аутентификации пользователя
                    # user.is_authenticated = True
                    # user.save()
                    user = authenticate(request, phone=phone_number)
                    if user:
                        login(request, user)

                    # return Response({'message': 'Аутентификация успешна'}, status=status.HTTP_200_OK)
                    return redirect('users:user-profile')
                else:
                    return Response({'error': 'Неверный код подтверждения'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'Укажите номер телефона и код подтверждения'},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    # def post(self, request):
    #     phone_number = request.data.get('phone_number')
    #     verification_code = request.data.get('verification_code')
    #
    #     if not phone_number or not verification_code:
    #         return Response({'error': 'Укажите номер телефона и код подтверждения'}, status=status.HTTP_400_BAD_REQUEST)
    #
    #     # Найти пользователя по номеру телефона
    #     user = get_object_or_404(User, phone=phone_number)
    #
    #     if not user:
    #         return JsonResponse({'error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)
    #
    #     # Найти последний сохраненный код подтверждения для данного пользователя
    #     user_code = UserCode.objects.filter(user=user).order_by('-created_at').first()
    #
    #     if not user_code:
    #         return Response({'error': 'Код подтверждения не найден'}, status=status.HTTP_404_NOT_FOUND)
    #
    #     # Выводим значения для сравнения в консоль
    #     print(f"Полученный код подтверждения: {verification_code}")
    #     print(f"Сохраненный код подтверждения: {user_code.sms_code}")
    #
    #     # Сравниваем полученный код с сохраненным кодом
    #     if str(user_code.sms_code) == str(verification_code):
    #         # Удалить использованный код подтверждения
    #         user_code.delete()
    #
    #         # Обновить статус аутентификации пользователя
    #         user.is_authenticated = True
    #         user.save()
    #
    #         # Перенаправить на страницу профиля
    #         return redirect('users:user_profile')
    #     else:
    #         return Response({'error': 'Неверный код подтверждения'}, status=status.HTTP_400_BAD_REQUEST)


class EnterSMSCodeView(TemplateView):
    template_name = 'users/enter_sms_code.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавьте здесь необходимые данные для отображения на странице
        return context
