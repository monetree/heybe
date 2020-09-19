from django.urls import path, include
from .views import (
    UserAuth,
    users,
    associated_playlists
)

urlpatterns = [
    path('user/register/', UserAuth.user_register),
    path('user/login/', UserAuth.user_login),
    path('user/forgot-password/', UserAuth.user_forgot_password),
    path('user/verify-otp/', UserAuth.user_verify_otp),
    path('user/reset-password/', UserAuth.user_reset_password),
    path('users/', users),
    path('user/associated-playlists/', associated_playlists),
]
