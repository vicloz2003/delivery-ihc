from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("email",)
    list_display = ("email", "role", "is_active", "is_staff")
    list_filter = ("role", "is_active", "is_staff")
    search_fields = ("email", "telegram_username", "telegram_chat_id")

    # Campos que se muestran en el formulario de edición del usuario
    fieldsets = (
        (None, {
            "fields": ("email", "password")
        }),
        (_("Rol y permisos"), {
            "fields": ("role", "is_active", "is_staff", "is_superuser", "groups", "user_permissions")
        }),
        (_("Información personal"), {
            "fields": ("phone", "telegram_chat_id", "telegram_username")
        }),
        (_("Fechas importantes"), {
            "fields": ("last_login", "date_joined")
        }),
    )

    # Campos para crear usuario desde el admin (sin username)
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "role", "is_staff", "is_active"),
        }),
    )

    # Eliminamos username porque no existe
    exclude = ("username",)
