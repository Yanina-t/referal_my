# views.py
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from users.models import User
from .forms import ProfileForm
from .serializers import PhoneAuthSerializer, UserProfileSerializer, VerifyCodeSerializer, ProfileEditSerializer
from .utils import create_user_with_verification_code, activate_invite_code
from django.contrib import messages
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

            # Вычисляем количество бонусов
            bonus_count = int(len(referral_users)) * 10

            # Создаем сериализатор для списка рефералов
            referral_serializer = UserProfileSerializer(referral_users, many=True)

            # Создаем сериализатор для данных пользователя
            user_serializer = ProfileEditSerializer(instance=user)

            # Передаем список рефералов и данные пользователя в контекст шаблона
            context = {
                'user': user,
                'referrals': referral_serializer.data,
                'serializer': user_serializer,
                'bonus_count': bonus_count
            }

            return Response(context, template_name=self.template_name)
        else:
            # Если пользователь не аутентифицирован, перенаправляем его на страницу входа
            return redirect('users:phone_auth')

    def get_referral_users(self, user):
        # Фильтруем пользователей по полю ref_user_id, где текущий пользователь является реферером
        referral_users = User.objects.filter(ref_user_id=user.id)
        return referral_users


@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user, files=request.FILES)
        if form.is_valid():
            form.save()
            return redirect('users:user_profile')  # Перенаправление на страницу профиля после сохранения
    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'users/editprofile_form.html', {'form': form})


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

        # Перенаправляем пользователя на страницу ввода SMS-кода
        return redirect('users:verify_code')


class VerifyCodeAPIView(APIView):
    """API-представление для проверки кода подтверждения."""

    def get(self, request):
        # Показать форму ввода кода подтверждения
        context = {}
        return render(request, 'users/verify_code.html', context)

    def post(self, request):
        serializer = VerifyCodeSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = request.session.get('phone_number')  # Получаем номер из сессии
            verification_code = serializer.validated_data.get('verification_code')

            if phone_number and verification_code:
                user = User.objects.filter(phone=phone_number).first()

                if not user:
                    messages.error(request, 'Пользователь не найден')
                    return redirect('users:phone_auth')  # Перенаправляем на страницу запроса нового кода

                if self.check_verification_code(user, verification_code):
                    # Если код подтверждения верен, выполнить аутентификацию
                    user.is_authenticated = True
                    user.save()

                    authenticated_user = authenticate(request, phone=phone_number)

                    if authenticated_user:
                        login(request, authenticated_user, backend='users.custom_auth.PhoneCodeAuthBackend')
                        return redirect('users:user_profile')
                    else:
                        messages.error(request, 'Ошибка аутентификации')
                        return redirect('users:phone_auth')
                else:
                    # Если код подтверждения неверен
                    messages.error(request, 'Неверный код подтверждения')
                    return redirect('users:verify_code')
            else:
                messages.error(request, 'Укажите номер телефона и код подтверждения')
                return redirect('users:verify_code')
        else:
            return HttpResponseBadRequest('Неверные данные в запросе')

    def check_verification_code(self, user, verification_code):
        """
        Проверка кода подтверждения пользователя.

        Args:
            user: объект пользователя.
            verification_code: код подтверждения для проверки.

        Returns:
            bool: True, если код подтверждения действителен для пользователя, иначе False.
        """
        user_code = user.usercode_set.order_by('-created_at').first()

        if user_code and str(user_code.sms_code) == str(verification_code):
            user_code.delete()  # Удаляем использованный код подтверждения
            return True
        else:
            return False


def activate_invite_code_view(request):
    if request.method == 'POST':
        invite_code = request.POST.get('invite_code')  # Получаем значение invite_code из POST-запроса
        current_user = request.user

        if not invite_code:
            # Если инвайт-код не указан, отправляем сообщение об ошибке
            messages.error(request, "Инвайт-код не указан")
            return HttpResponseBadRequest("Инвайт-код не указан")

        # Попытка активировать инвайт-код
        activated = activate_invite_code(current_user, invite_code)

        if activated:
            return HttpResponseRedirect(reverse('users:user_profile'))
        else:
            # Если активация не удалась, отправляем сообщение об ошибке
            messages.error(request, "Несуществующий или недействительный инвайт-код")
            return HttpResponseRedirect(reverse('users:user_profile'))

    # Если метод запроса не поддерживается (например, GET), отправляем сообщение об ошибке
    messages.error(request, "Метод запроса не поддерживается")
    return HttpResponseBadRequest("Метод запроса не поддерживается")


class LogoutView(View):
    def get(self, request):
        # Обработка GET запроса (например, для перехода на страницу выхода)
        return redirect(reverse_lazy('users:home'))  # Перенаправление на главную страницу

    def post(self, request):
        if request.user.is_authenticated:
            # Установка атрибута is_authenticated на False
            request.user.is_authenticated = False
            request.user.save()  # Сохранение изменений
            logout(request)  # Выход пользователя из системы
            return redirect('users:home')  # Перенаправление на главную страницу
        else:
            # Если пользователь не был аутентифицирован, перенаправляем на главную страницу
            return redirect('users:home')
