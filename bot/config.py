"""
Configuración del Bot de Telegram - SIMPLIFICADO
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Token del bot
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'TU_TOKEN_AQUI')

# URL base de la API
API_URL = os.getenv('API_URL', 'http://localhost:8000/api')

# Token secreto para autenticación
BOT_SECRET = os.getenv('BOT_SECRET', 'your-super-secret-token-change-in-production')

# Timeout para requests
REQUEST_TIMEOUT = 10

# Estados del flujo
class States:
    MENU = 'menu'
    SELECCIONANDO_PRODUCTO = 'seleccionando_producto'
    CANTIDAD = 'cantidad'
    OBSERVACIONES = 'observaciones'
    CARRITO = 'carrito'
    CONFIRMANDO = 'confirmando'
    UBICACION = 'ubicacion'
    PAGO = 'pago'
    ESPERANDO_PAGO = 'esperando_pago'
    COMPLETADO = 'completado'