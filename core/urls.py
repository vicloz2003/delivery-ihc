# users/urls.py
from django.urls import path
from .views import (
    LoginView, 
    RegisterView, 
    MeView, 
    LinkTelegramView,
    TelegramAuthView,
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Autenticación tradicional
    path('login/', LoginView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='register'),
    
    # Perfil de usuario
    path('me/', MeView.as_view(), name='me'),
    

    path('telegram/link/', LinkTelegramView.as_view(), name='telegram-link'),
    path('telegram/auth/', TelegramAuthView.as_view(), name='telegram-auth'),
]