"""
Manejadores del bot - SOLO FLUJO DEL DOCUMENTO
"""
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from .api_client import APIClient
from .keyboards import (
    menu_inicio, menu_productos, menu_cantidad, menu_observaciones,
    menu_carrito, menu_ubicacion, menu_pago
)
from .config import States

api = APIClient()

# Almacenar sesiones (en producción usar BD)
user_data = {}


def get_user_data(user_id):
    """Obtener datos del usuario"""
    if user_id not in user_data:
        user_data[user_id] = {
            'token': None,
            'carrito': [],
            'subtotal': 0,
            'pedido': None
        }
    return user_data[user_id]


# =============== INICIO ===============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start - Autenticación automática"""
    user_id = update.effective_user.id
    username = update.effective_user.username or "usuario"
    
    # Autenticarse con Telegram
    resultado = api.telegram_auth(str(user_id), username)
    
    if resultado and resultado.get('user'):
        datos = get_user_data(user_id)
        datos['token'] = resultado.get('access')
        datos['user_id'] = resultado['user']['id']
        
        mensaje = f"👋 ¡Hola {resultado['user']['email']}!\n\n¿Qué deseas?"
        await update.message.reply_text(mensaje, reply_markup=menu_inicio())
        return States.MENU
    else:
        await update.message.reply_text("❌ Error de autenticación")
        return ConversationHandler.END


# =============== 1. VER MENÚ ===============

async def ver_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostrar menú"""
    user_id = update.effective_user.id
    
    menu_data = api.get_menu()
    
    if not menu_data:
        await update.message.reply_text("❌ Error al obtener el menú")
        return States.MENU
    
    categorias = menu_data.get('categories', [])
    
    # Mostrar cada categoría
    for categoria in categorias:
        productos = categoria.get('products', [])
        
        texto = f"*{categoria['name']}*\n\n"
        for prod in productos:
            texto += f"• {prod['name']} - Bs. {prod['price']}\n"
        
        keyboard = menu_productos(productos)
        await update.message.reply_text(texto, parse_mode='Markdown', reply_markup=keyboard)
    
    await update.message.reply_text(
        "Haz clic en el producto que deseas",
        reply_markup=menu_inicio()
    )
    return States.SELECCIONANDO_PRODUCTO


# =============== 2. SELECCIONAR PRODUCTO ===============

async def seleccionar_producto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Usuario clickea en producto"""
    user_id = update.effective_user.id
    query = update.callback_query
    
    # Obtener ID del producto
    product_id = int(query.data.split('_')[1])
    
    # Buscar producto en menú
    menu_data = api.get_menu()
    producto_encontrado = None
    
    for categoria in menu_data.get('categories', []):
        for prod in categoria.get('products', []):
            if prod['id'] == product_id:
                producto_encontrado = prod
                break
    
    if producto_encontrado:
        datos = get_user_data(user_id)
        datos['producto_actual'] = producto_encontrado
        
        await query.answer()
        await query.edit_message_text(
            f"*{producto_encontrado['name']}*\n\n¿Cuántos deseas? ({producto_encontrado['description']})",
            parse_mode='Markdown',
            reply_markup=menu_cantidad()
        )
        return States.CANTIDAD
    
    return States.SELECCIONANDO_PRODUCTO


# =============== 3. CANTIDAD ===============

async def seleccionar_cantidad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Usuario ingresa cantidad"""
    user_id = update.effective_user.id
    cantidad_text = update.message.text
    
    datos = get_user_data(user_id)
    
    try:
        cantidad = int(cantidad_text)
    except ValueError:
        await update.message.reply_text("❌ Ingresa un número válido")
        return States.CANTIDAD
    
    datos['cantidad_actual'] = cantidad
    
    await update.message.reply_text(
        "¿Alguna observación? (ej: sin cebolla, extra picante)\n\nEscribe 'ninguna' si no hay",
        reply_markup=menu_observaciones()
    )
    return States.OBSERVACIONES


# =============== 4. OBSERVACIONES ===============

async def agregar_observaciones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Usuario agrega observaciones"""
    user_id = update.effective_user.id
    observacion = update.message.text
    
    datos = get_user_data(user_id)
    producto = datos['producto_actual']
    cantidad = datos['cantidad_actual']
    
    # Agregar al carrito
    item = {
        'product_id': producto['id'],
        'quantity': cantidad,
        'notes': observacion if observacion != 'ninguna' else ''
    }
    
    datos['carrito'].append(item)
    datos['subtotal'] += producto['price'] * cantidad
    
    # Mostrar carrito
    texto = "🛒 *Tu Carrito*\n\n"
    for idx, item_carrito in enumerate(datos['carrito'], 1):
        # Buscar producto para obtener nombre y precio
        menu_data = api.get_menu()
        for cat in menu_data.get('categories', []):
            for prod in cat.get('products', []):
                if prod['id'] == item_carrito['product_id']:
                    subtotal = prod['price'] * item_carrito['quantity']
                    texto += f"{idx}. {item_carrito['quantity']}x {prod['name']} - Bs. {subtotal}\n"
                    if item_carrito['notes']:
                        texto += f"   Nota: {item_carrito['notes']}\n"
    
    texto += f"\n*Subtotal: Bs. {datos['subtotal']:.2f}*"
    
    await update.message.reply_text(texto, parse_mode='Markdown', reply_markup=menu_carrito())
    return States.CARRITO


# =============== 5. CARRITO ===============

async def procesar_carrito(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Usuario elige qué hacer con el carrito"""
    user_id = update.effective_user.id
    opcion = update.message.text
    
    if opcion == "➕ Agregar Más":
        # Volver a mostrar menú
        await ver_menu(update, context)
        return States.SELECCIONANDO_PRODUCTO
    
    elif opcion == "✅ Confirmar Pedido":
        # Pasar a ubicación
        await update.message.reply_text(
            "📍 *Compartir Ubicación de Entrega*\n\nPor favor, comparte tu ubicación actual",
            parse_mode='Markdown',
            reply_markup=menu_ubicacion()
        )
        return States.UBICACION
    
    elif opcion == "❌ Cancelar":
        # Limpiar carrito
        datos = get_user_data(user_id)
        datos['carrito'] = []
        datos['subtotal'] = 0
        
        await update.message.reply_text("Pedido cancelado", reply_markup=menu_inicio())
        return States.MENU


# =============== 6. UBICACIÓN ===============

async def recibir_ubicacion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Usuario comparte ubicación"""
    user_id = update.effective_user.id
    
    if not update.message.location:
        await update.message.reply_text("❌ Por favor, comparte tu ubicación")
        return States.UBICACION
    
    ubicacion = update.message.location
    datos = get_user_data(user_id)
    
    datos['lat'] = ubicacion.latitude
    datos['lon'] = ubicacion.longitude
    
    # Crear pedido en API
    resultado = api.create_order(
        token=datos['token'],
        lat=datos['lat'],
        lon=datos['lon'],
        items=datos['carrito']
    )
    
    if resultado:
        datos['pedido'] = resultado
        
        texto = f"✅ *PEDIDO CREADO*\n\n"
        texto += f"Pedido: {resultado['order_number']}\n"
        texto += f"Total: Bs. {resultado['total']}\n"
        texto += f"Estado: {resultado['status_display']}\n\n"
        texto += "Por favor, realiza el pago con el código QR"
        
        await update.message.reply_text(texto, parse_mode='Markdown', reply_markup=menu_pago())
        return States.PAGO
    else:
        await update.message.reply_text("❌ Error al crear pedido")
        return States.UBICACION


# =============== 7. PAGO ===============

async def procesar_pago(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Usuario confirma pago"""
    user_id = update.effective_user.id
    opcion = update.message.text
    
    datos = get_user_data(user_id)
    pedido = datos['pedido']
    
    if opcion == "✅ Pagar con QR":
        # TODO: Mostrar código QR (en app payments)
        texto = f"🎟️ *PAGO*\n\n"
        texto += f"Pedido: {pedido['order_number']}\n"
        texto += f"Total: Bs. {pedido['total']}\n\n"
        texto += "QR Code aquí (implementar después)\n\n"
        texto += "Recibirás confirmación cuando se procese el pago"
        
        await update.message.reply_text(texto, parse_mode='Markdown')
        
        # Ver estado
        return await ver_estado_pedido(update, context, datos['token'], pedido['id'])
    
    elif opcion == "❌ Cancelar":
        await update.message.reply_text("Pago cancelado", reply_markup=menu_inicio())
        return States.MENU


# =============== 8. VER ESTADO ===============

async def ver_estado_pedido(update: Update, context: ContextTypes.DEFAULT_TYPE, token=None, order_id=None):
    """Ver estado del pedido"""
    user_id = update.effective_user.id
    
    datos = get_user_data(user_id)
    
    if not token:
        token = datos.get('token')
    if not order_id:
        order_id = datos.get('pedido', {}).get('id')
    
    if not token or not order_id:
        await update.message.reply_text("❌ No hay pedido para mostrar")
        return States.MENU
    
    pedido = api.get_order(token, order_id)
    
    if pedido:
        emoji_estado = {
            'pending': '⏳',
            'confirmed': '✅',
            'preparing': '👨‍🍳',
            'ready': '📦',
            'in_transit': '🚗',
            'delivered': '✅'
        }
        
        emoji = emoji_estado.get(pedido['status'], '❓')
        
        texto = f"📦 *ESTADO DEL PEDIDO*\n\n"
        texto += f"Pedido: {pedido['order_number']}\n"
        texto += f"Estado: {emoji} {pedido['status_display']}\n"
        texto += f"Total: Bs. {pedido['total']}\n"
        
        await update.message.reply_text(texto, parse_mode='Markdown', reply_markup=menu_inicio())
        return States.MENU
    else:
        await update.message.reply_text("❌ Error al obtener estado")
        return States.MENU