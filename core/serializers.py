# users/serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User


class EmailLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(email=email, password=password)

        if not user:
            raise serializers.ValidationError("Credenciales inválidas")
        
        # ✅ NUEVO: Verificar si el usuario está activo
        if not user.is_active:
            raise serializers.ValidationError("Usuario inactivo")

        attrs["user"] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    # ✅ NUEVO: Campo calculado para mostrar el nombre del rol
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = User
        fields = [
            "id", 
            "email", 
            "role", 
            "role_display",  # ✅ Nuevo
            "phone", 
            "telegram_chat_id", 
            "telegram_username",
            "is_telegram_verified",  # ✅ Nuevo
            "created_at",  # ✅ Nuevo
        ]
        read_only_fields = ["id", "created_at"]


class UserRegisterSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(write_only=True)  # ✅ Confirmación de password
    
    class Meta:
        model = User
        fields = ["email", "password", "password_confirm", "role", "phone"]
        extra_kwargs = {
            "password": {"write_only": True, "min_length": 8}  # ✅ Longitud mínima
        }

    def validate(self, attrs):
      
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden"})
        
        
        email = attrs.get('email', '').lower()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "Este email ya está registrado"})
        
        return attrs

    def create(self, validated_data):
        # Remover password_confirm
        validated_data.pop('password_confirm', None)
        
        user = User.objects.create(
            email=validated_data["email"].lower(),  # ✅ Email en minúsculas
            role=validated_data.get("role", "CUSTOMER"),
            phone=validated_data.get("phone", "")
        )
        user.set_password(validated_data["password"])
        user.save()
        return user



class TelegramLinkSerializer(serializers.Serializer):
    """Para vincular cuenta de Telegram con usuario existente"""
    telegram_chat_id = serializers.CharField()
    telegram_username = serializers.CharField(required=False, allow_blank=True)
    
    def validate_telegram_chat_id(self, value):
        # Verificar que no esté ya vinculado
        if User.objects.filter(telegram_chat_id=value).exclude(id=self.context.get('user_id')).exists():
            raise serializers.ValidationError("Este Telegram ya está vinculado a otra cuenta")
        return value