# #urls.py
# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from users.views import PhoneAuthAPIView, UserLoginAPIView, UserViewSet, MyTokenObtainPairView, VerifyCodeAPIView
#
# app_name = 'users'
#
# # Описание маршрутизации для ViewSet
# router = DefaultRouter()
# router.register(r'user', UserViewSet, basename='user')
#
# urlpatterns = [
#     path('register/', PhoneAuthAPIView.as_view(), name='user_registration'),
#     path('users/verify/', VerifyCodeAPIView.as_view(), name='verify_code'),
#     path('login/', UserLoginAPIView.as_view(), name='user_login'),
#     path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
#     path('', include(router.urls)),  # Включаем URL маршруты для ViewSet
# ]

from django.urls import path
from users.views import PhoneAuthAPIView, VerifyCodeAPIView

urlpatterns = [
    path('register/', PhoneAuthAPIView.as_view(), name='user_registration'),
    path('verify/', VerifyCodeAPIView.as_view(), name='verify_code'),
]
