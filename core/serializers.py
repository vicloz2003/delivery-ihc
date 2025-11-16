from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User


# -------------------------------------------------------
# Serializer: LOGIN (email + password)
# -------------------------------------------------------
class EmailLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(email=email, password=password)

        if not user:
            raise serializers.ValidationError("Credenciales inválidas")

        attrs["user"] = user
        return attrs


# -------------------------------------------------------
# Serializer: Información básica de usuario
# -------------------------------------------------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "role", "phone", "telegram_chat_id", "telegram_username"]


# -------------------------------------------------------
# Serializer: Registro de usuario (opcional)
# Lo usaremos si deseas que el BOT registre clientes.
# -------------------------------------------------------
class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "password", "role"]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def create(self, validated_data):
        # Crea usuario con password encriptado
        user = User.objects.create(
            email=validated_data["email"],
            role=validated_data.get("role", "CUSTOMER")
        )
        user.set_password(validated_data["password"])
        user.save()
        return user
