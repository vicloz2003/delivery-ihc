from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('CUSTOMER', 'Cliente'),
        ('DRIVER', 'Conductor'),
    )

    # Deshabilitamos username
    username = None

    # Usamos email como identificador para login
    email = models.EmailField(unique=True)

    # Rol del usuario
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CUSTOMER')

    # Otros datos
    phone = models.CharField(max_length=20, blank=True, null=True)

    # Campos para integración con Telegram
    telegram_chat_id = models.CharField(max_length=50, blank=True, null=True, unique=True)
    telegram_username = models.CharField(max_length=100, blank=True, null=True)

    # Configuración fundamental del CustomUser
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # No pedimos username al crear usuario

    def __str__(self):
        return f"{self.email} ({self.role})"
