from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """Manager personalizado para el modelo User sin username"""
    
    def create_user(self, email, password=None, **extra_fields):
        """Crear y guardar un usuario regular"""
        if not email:
            raise ValueError('El email es obligatorio')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Crear y guardar un superusuario"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    ROLE_CHOICES = (
        ('CUSTOMER', 'Cliente'),
        ('DRIVER', 'Conductor'),
    )

    # Deshabilitamos username
    username = None

    # Usamos email como identificador para login
    email = models.EmailField(unique=True, db_index=True)

    # Rol del usuario
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CUSTOMER')

    # Otros datos
    phone = models.CharField(max_length=20, blank=True, null=True)

    # Campos para integración con Telegram
    telegram_chat_id = models.CharField(max_length=50, blank=True, null=True, unique=True, db_index=True)
    telegram_username = models.CharField(max_length=100, blank=True, null=True)
    
    # Campo para saber si el usuario completó el registro
    is_telegram_verified = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Configuración fundamental del CustomUser
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    # Asignar el manager personalizado
    objects = UserManager()

    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['telegram_chat_id']),
        ]

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"