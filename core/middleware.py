# users/middleware.py

import hmac
import hashlib
import json
from urllib.parse import parse_qsl
from django.conf import settings
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from .models import User


def validate_telegram_webapp_data(init_data: str, bot_token: str) -> dict | None:
    """
    Valida el initData de Telegram Web App según documentación oficial
    https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
    
    Returns:
        dict con datos del usuario si es válido
        None si la validación falla
    """
    try:
        # Parsear el init_data
        parsed_data = dict(parse_qsl(init_data))
        
        # Extraer el hash recibido
        received_hash = parsed_data.pop('hash', None)
        if not received_hash:
            return None
        
        # Crear data_check_string
        data_check_string_parts = []
        for key in sorted(parsed_data.keys()):
            data_check_string_parts.append(f"{key}={parsed_data[key]}")
        data_check_string = '\n'.join(data_check_string_parts)
        
        # Crear secret_key
        secret_key = hmac.new(
            key=b"WebAppData",
            msg=bot_token.encode(),
            digestmod=hashlib.sha256
        ).digest()
        
        # Calcular hash esperado
        calculated_hash = hmac.new(
            key=secret_key,
            msg=data_check_string.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()
        
               # Verificar que coincidan
        if calculated_hash != received_hash:
            print(f"[DEBUG-HASH] ❌ Hash mismatch!\n  calculated: {calculated_hash}\n  received:   {received_hash}")
            return None
        else:
            print(f"[DEBUG-HASH] ✅ Hash OK")
        
        # Parsear datos del usuario
        user_data = json.loads(parsed_data.get('user', '{}'))
        
        return {
            'id': user_data.get('id'),
            'first_name': user_data.get('first_name', ''),
            'last_name': user_data.get('last_name', ''),
            'username': user_data.get('username', ''),
            'language_code': user_data.get('language_code', 'en'),
        }
        
    except Exception as e:
        print(f"Error validating Telegram init data: {e}")
        return None


class TelegramWebAppAuthMiddleware(MiddlewareMixin):
    """
    Middleware para autenticar requests de Telegram Mini Apps
    
    - Valida el initData en header X-Telegram-Init-Data
    - Busca o crea el usuario automáticamente
    - Asigna request.user
    """
    
    # Rutas que NO requieren autenticación
    EXEMPT_PATHS = [
        '/admin/',
        '/api/users/telegram/auth/',
        '/api/users/login/',
        '/api/users/register/',
        '/static/',
        '/media/',
    ]
    
    # Rutas públicas (GET only)
    PUBLIC_GET_PATHS = [
        '/api/menu/categories/bot-menu/',
        '/api/menu/products/available/',
    ]
    
    def process_request(self, request):
        # Saltar rutas exentas
        if any(request.path.startswith(path) for path in self.EXEMPT_PATHS):
            return None
        
        # Permitir GET en rutas públicas
        if request.method == 'GET' and any(request.path.startswith(path) for path in self.PUBLIC_GET_PATHS):
            return None
        
        # Solo validar en rutas de API
        if not request.path.startswith('/api/'):
            return None
        
        # Obtener initData del header
        init_data = request.META.get('HTTP_X_TELEGRAM_INIT_DATA')
        
        if not init_data:
            return JsonResponse({
                'error': 'Missing Telegram authentication data',
                'detail': 'X-Telegram-Init-Data header is required'
            }, status=401)
        
               # Validar initData
        bot_token = settings.TELEGRAM_BOT_TOKEN
        print(f"[DEBUG-MIDDLEWARE] bot_token presente: {bool(bot_token)}, primeros 10 chars: {bot_token[:10] if bot_token else 'None'}")
        print(f"[DEBUG-MIDDLEWARE] init_data primeros 80 chars: {init_data[:80]}")
        validated_data = validate_telegram_webapp_data(init_data, bot_token)
        
        if not validated_data:
            print(f"[DEBUG-MIDDLEWARE] ❌ Validación FALLÓ - hash HMAC no coincide o error en parseo")
            return JsonResponse({
                'error': 'Invalid Telegram authentication data',
                'detail': 'InitData signature verification failed'
            }, status=403)
        else:
            print(f"[DEBUG-MIDDLEWARE] ✅ Validación OK - usuario ID: {validated_data.get('id')}")
        
        # Buscar o crear usuario
        telegram_id = str(validated_data['id'])
        
        try:
            user = User.objects.get(telegram_chat_id=telegram_id)
            
            # Actualizar datos si cambiaron
            updated = False
            if user.telegram_username != validated_data['username']:
                user.telegram_username = validated_data['username']
                updated = True
            if user.first_name != validated_data['first_name']:
                user.first_name = validated_data['first_name']
                updated = True
            if user.last_name != validated_data['last_name']:
                user.last_name = validated_data['last_name']
                updated = True
            
            if updated:
                user.save()
                
        except User.DoesNotExist:
            # Crear usuario automáticamente
            user = User.objects.create(
                telegram_chat_id=telegram_id,
                telegram_username=validated_data['username'],
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
                email=f'telegram_{telegram_id}@temp.com',
                role='CUSTOMER',
                is_telegram_verified=True,
            )
        
        # Asignar usuario al request
        request.user = user
        request.telegram_data = validated_data
        
        return None