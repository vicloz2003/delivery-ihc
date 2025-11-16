from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import (
    EmailLoginSerializer,
    UserSerializer,
    UserRegisterSerializer,
)


# -------------------------------------------------------
# Login por email + password
# -------------------------------------------------------
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
        })


# -------------------------------------------------------
# Refresh token
# -------------------------------------------------------
from rest_framework_simplejwt.views import TokenRefreshView


# -------------------------------------------------------
# Registrar usuario (opcional)
# -------------------------------------------------------
class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]


# -------------------------------------------------------
# Obtener perfil del usuario autenticado
# -------------------------------------------------------
class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
