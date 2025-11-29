# delivery-ihc/core/auth.py
import logging
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import authentication, exceptions

from .middleware import validate_telegram_webapp_data  # usa la función existente

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

        # validate_telegram_webapp_data should return parsed dict on success,
        # or False/None on failure. Adapt if your function returns a User.
        parsed = validate_telegram_webapp_data(init_data, bot_token)
        if not parsed:
            raise exceptions.AuthenticationFailed("Invalid Telegram init data")

        # parsed is expected to contain a 'user' JSON or at least an 'id' for telegram user
        telegram_user = None
        if isinstance(parsed, dict):
            telegram_user = parsed.get("user") or parsed.get("tg_user") or parsed
        elif hasattr(parsed, "id"):
            # If validate_telegram_webapp_data already returns a Django user instance
            return (parsed, None)

        if not telegram_user:
            raise exceptions.AuthenticationFailed("Telegram init data missing user info")

        tg_id = None
        if isinstance(telegram_user, dict):
            tg_id = telegram_user.get("id")
            first_name = telegram_user.get("first_name") or ""
        else:
            # fallback: if an object with id attribute
            tg_id = getattr(telegram_user, "id", None)
            first_name = getattr(telegram_user, "first_name", "") or ""

        if not tg_id:
            raise exceptions.AuthenticationFailed("Telegram user id not found in init data")

        # Create or get a local Django user representing this Telegram user.
        username = f"tg_{tg_id}"
        try:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"first_name": first_name},
            )
            if created:
                logger.info("Created local user for Telegram id %s -> %s", tg_id, username)
        except Exception as exc:
            logger.exception("Error getting/creating user for Telegram id %s: %s", tg_id, exc)
            raise exceptions.AuthenticationFailed("Internal error during Telegram auth")

        # Ensure request caching aligns with middleware approach
        try:
            request._cached_user = user
        except Exception:
            setattr(request, "_cached_user", user)

        logger.debug("[DEBUG-AUTH] Authenticated via TelegramHeaderAuthentication: %s", username)
        return (user, None)