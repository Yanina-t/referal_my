from . import views
from django.urls import path
from users.views import (
    PhoneAuthAPIView,
    VerifyCodeAPIView,
    UserProfileAPIView,
    HomePageView,
)

app_name = 'users'

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('phone-auth/', PhoneAuthAPIView.as_view(), name='phone_auth'),
    path('verify-code/', VerifyCodeAPIView.as_view(), name='verify_code'),
    path('user-profile/', UserProfileAPIView.as_view(), name='user_profile'),
    path('activate-invite-code/', views.activate_invite_code_view, name='activate_invite_code'),
]
