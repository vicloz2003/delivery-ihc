"""
Teclados para el bot - SIMPLIFICADO
"""
from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def menu_inicio():
    """Menú principal"""
    keyboard = [
        [KeyboardButton("🍔 Ver Menú")],
        [KeyboardButton("📦 Ver Mi Pedido")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)


def menu_productos(productos):
    """Menú dinámico de productos"""
    keyboard = []
    for prod in productos:
        keyboard.append([
            InlineKeyboardButton(
                f"{prod['name']} - Bs. {prod['price']}", 
                callback_data=f"prod_{prod['id']}"
            )
        ])
    return InlineKeyboardMarkup(keyboard)


def menu_cantidad():
    """Seleccionar cantidad"""
    keyboard = [
        [KeyboardButton(str(i)) for i in range(1, 6)],
        [KeyboardButton("Otra")],
        [KeyboardButton("❌ Cancelar")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def menu_observaciones():
    """Agregar observaciones"""
    keyboard = [
        [KeyboardButton("Sin observaciones")],
        [KeyboardButton("Escribir nota")],
        [KeyboardButton("⬅️ Atrás")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def menu_carrito():
    """Acciones del carrito"""
    keyboard = [
        [KeyboardButton("➕ Agregar Más")],
        [KeyboardButton("✅ Confirmar Pedido")],
        [KeyboardButton("❌ Cancelar")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def menu_ubicacion():
    """Compartir ubicación"""
    keyboard = [
        [KeyboardButton("📍 Compartir Ubicación", request_location=True)],
        [KeyboardButton("❌ Cancelar")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def menu_pago():
    """Confirmar pago"""
    keyboard = [
        [KeyboardButton("✅ Pagar con QR")],
        [KeyboardButton("❌ Cancelar")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)