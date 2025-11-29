# delivery-ihc/core/auth.py
import logging
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import authentication, exceptions

from core.middleware import validate_telegram_webapp_data  # ajusta el import si es otra ruta

logger = logging.getLogger(__name__)
User = get_user_model()

class TelegramHeaderAuthentication(authentication.BaseAuthentication):
    """
    Authenticate requests that include the X-Telegram-Init-Data header.
    If present and valid, returns (user, None). Otherwise returns None
    so DRF falls back to the next authentication class.
    """
    def authenticate(self, request):
        init_data = request.META.get("HTTP_X_TELEGRAM_INIT_DATA")
        if not init_data:
            return None

        bot_token = getattr(settings, "TELEGRAM_BOT_TOKEN", None)
        if not bot_token:
            logger.warning("TelegramHeaderAuthentication: TELEGRAM_BOT_TOKEN not set")
            return None

        validated = validate_telegram_webapp_data(init_data, bot_token)
        if not validated:
            raise exceptions.AuthenticationFailed("Invalid Telegram init data")

        # validated is expected to be a dict with keys: id, first_name, last_name, username, language_code
        tg_id = validated.get("id")
        if not tg_id:
            raise exceptions.AuthenticationFailed("Telegram user id not found in init data")

        tg_username = validated.get("username", "") or ""
        first_name = validated.get("first_name", "") or ""
        last_name = validated.get("last_name", "") or ""

        # Use telegram_chat_id as the unique identifier in local User model
        try:
            user, created = User.objects.get_or_create(
                telegram_chat_id=str(tg_id),
                defaults={
                    "telegram_username": tg_username,
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": f"telegram_{tg_id}@temp.com",
                    "role": "CUSTOMER",
                    "is_telegram_verified": True,
                },
            )
            if not created:
                # keep user data in sync if desired (optional)
                updated = False
                if user.telegram_username != tg_username:
                    user.telegram_username = tg_username
                    updated = True
                if user.first_name != first_name:
                    user.first_name = first_name
                    updated = True
                if user.last_name != last_name:
                    user.last_name = last_name
                    updated = True
                if updated:
                    user.save()

        except Exception as exc:
            logger.exception("Error getting/creating user for Telegram id %s: %s", tg_id, exc)
            raise exceptions.AuthenticationFailed("Internal error during Telegram auth")

        # Ensure DRF/get_user cache reflects this user
        try:
            request._cached_user = user  # some code uses this cache
        except Exception:
            setattr(request, "_cached_user", user)

        logger.debug("[DEBUG-AUTH] Authenticated via TelegramHeaderAuthentication: tg_%s", tg_id)
        return (user, None)