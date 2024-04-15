# views.py
from django.contrib.auth import authenticate, login
from django.http import JsonResponse, HttpResponseRedirect, HttpResponseNotAllowed, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView
from rest_framework.generics import get_object_or_404, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from users.models import User, UserCode
from .serializers import PhoneAuthSerializer, UserProfileSerializer, VerifyCodeSerializer, ProfileEditSerializer, \
    ReferralSerializer
from .utils import create_user_with_verification_code, activate_invite_code
from rest_framework import generics
from django.contrib import messages
from django.contrib.messages import constants as messages_constants
from rest_framework.renderers import TemplateHTMLRenderer


class HomePageView(View):
    def get(self, request):
        return render(request, 'users/home.html')


class UserProfileAPIView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'users/profile.html'

    def get(self, request):
        # Проверяем аутентификацию пользователя
        if request.user.is_authenticated:
            user = request.user

            # Получаем список рефералов текущего пользователя
            referral_users = self.get_referral_users(user)

            # Создаем сериализатор для списка рефералов
            referral_serializer = UserProfileSerializer(referral_users, many=True)

            # Создаем сериализатор для данных пользователя
            user_serializer = ProfileEditSerializer(instance=user)

            # Передаем список рефералов и данные пользователя в контекст шаблона
            context = {
                'user': user,
                'referrals': referral_serializer.data,
                'serializer': user_serializer
            }

            return Response(context, template_name=self.template_name)
        else:
            # Если пользователь не аутентифицирован, перенаправляем его на страницу входа
            return redirect('users:phone_auth')

    def get_referral_users(self, user):
        # Фильтруем пользователей по полю ref_user_id, где текущий пользователь является реферером
        referral_users = User.objects.filter(ref_user_id=user.id)
        return referral_users

#
# class ReferralListView(generics.ListAPIView):
#     """Представление для вывода списка рефералов пользователя."""
#     permission_classes = [IsAuthenticated]
#
#     def get_queryset(self):
#         # Получаем текущего пользователя из аутентифицированного запроса
#         user = self.request.user
#
#         # Фильтруем пользователей по полю ref_user_id, где текущий пользователь является реферером
#         referral_users = User.objects.filter(ref_user_id=user.id)
#
#         return referral_users


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
        request.session.clear()

        try:
            # Сохраняем номер телефона в сессии для последующих запросов
            request.session['phone_number'] = phone_number

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
        # Показать форму ввода кода подтверждения
        context = {}
        return render(request, 'users/verify_code.html', context)

    def post(self, request):
        serializer = VerifyCodeSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = request.session.get('phone_number') # Получаем номер из сессии
            verification_code = serializer.validated_data.get('verification_code')

            # Далее логика для проверки кода подтверждения
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
                    return redirect('users:user_profile')
                else:
                    return Response({'error': 'Неверный код подтверждения'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'Укажите номер телефона и код подтверждения'},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def activate_invite_code_view(request):
    if request.method == 'POST':
        invite_code = request.POST.get('invite_code')  # Получаем значение invite_code из POST-запроса
        current_user = request.user

        if not invite_code:
            # Если инвайт-код не указан, отправляем сообщение об ошибке
            messages.error(request, "Инвайт-код не указан")
            return HttpResponseBadRequest("Инвайт-код не указан")

        print(f"Полученный invite_code: {invite_code}")
        print(f"Текущий пользователь: {current_user}")

        # Попытка активировать инвайт-код
        activated = activate_invite_code(current_user, invite_code)

        if activated:
            # Если инвайт-код успешно активирован, отправляем сообщение об успехе и перенаправляем пользователя
            messages.success(request, "Инвайт-код успешно активирован")
            return HttpResponseRedirect(reverse('users:user_profile'))
        else:
            # Если активация не удалась, отправляем сообщение об ошибке
            messages.error(request, "Ошибка активации инвайт-кода")
            return HttpResponseBadRequest("Ошибка активации инвайт-кода")

    # Если метод запроса не поддерживается (например, GET), отправляем сообщение об ошибке
    messages.error(request, "Метод запроса не поддерживается")
    return HttpResponseBadRequest("Метод запроса не поддерживается")






