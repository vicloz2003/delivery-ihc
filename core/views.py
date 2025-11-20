# users/views.py
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import (
    EmailLoginSerializer,
    UserSerializer,
    UserRegisterSerializer,
    TelegramLinkSerializer,
)


class LoginView(generics.GenericAPIView):
    serializer_class = EmailLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)

        return Response({
            "user": UserSerializer(user).data,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }, status=status.HTTP_200_OK)


class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # ✅ Generar tokens automáticamente
        refresh = RefreshToken.for_user(user)
        
        return Response({
            "user": UserSerializer(user).data,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "message": "Usuario registrado exitosamente"
        }, status=status.HTTP_201_CREATED)


class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user



class LinkTelegramView(APIView):
    """Vincular cuenta de Telegram al usuario autenticado"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = TelegramLinkSerializer(
            data=request.data, 
            context={'user_id': request.user.id}
        )
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        user.telegram_chat_id = serializer.validated_data['telegram_chat_id']
        user.telegram_username = serializer.validated_data.get('telegram_username', '')
        user.is_telegram_verified = True
        user.save()
        
        return Response({
            "message": "Telegram vinculado exitosamente",
            "user": UserSerializer(user).data
        }, status=status.HTTP_200_OK)



class TelegramAuthView(APIView):
    """
    Endpoint especial para que el bot de Telegram cree/obtenga usuarios
    Requiere un token secreto en lugar de JWT
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        # ✅ Validar token secreto del bot
        bot_token = request.headers.get('X-Bot-Token')
        from django.conf import settings
        
        if bot_token != getattr(settings, 'TELEGRAM_BOT_SECRET', 'your-secret-token'):
            return Response(
                {"error": "Token de bot inválido"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        telegram_chat_id = request.data.get('telegram_chat_id')
        telegram_username = request.data.get('telegram_username', '')
        
        if not telegram_chat_id:
            return Response(
                {"error": "telegram_chat_id es requerido"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Buscar o crear usuario
        user, created = User.objects.get_or_create(
            telegram_chat_id=telegram_chat_id,
            defaults={
                'email': f'telegram_{telegram_chat_id}@temp.com',  # Email temporal
                'telegram_username': telegram_username,
                'role': 'CUSTOMER',
                'is_telegram_verified': True,
            }
        )
        
        if not created:
            # Actualizar username si cambió
            user.telegram_username = telegram_username
            user.save()
        
        return Response({
            "user": UserSerializer(user).data,
            "created": created
        }, status=status.HTTP_200_OK if not created else status.HTTP_201_CREATED)