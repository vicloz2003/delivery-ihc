"""
Bot de Telegram - SIMPLIFICADO
Ejecutar: python bot/main.py
"""
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, filters
from telegram import Update

from .config import BOT_TOKEN, States
from .handlers import (
    start,
    ver_menu,
    seleccionar_producto,
    seleccionar_cantidad,
    agregar_observaciones,
    procesar_carrito,
    recibir_ubicacion,
    procesar_pago,
    ver_estado_pedido
)

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    """Iniciar el bot"""
    
    if not BOT_TOKEN or BOT_TOKEN == 'TU_TOKEN_AQUI':
        print("❌ ERROR: Token del bot no configurado")
        print("Solución: Agrega TELEGRAM_BOT_TOKEN en .env")
        return
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            States.MENU: [
                MessageHandler(filters.Regex('^🍔 Ver Menú$'), ver_menu),
                MessageHandler(filters.Regex('^📦 Ver Mi Pedido$'), ver_estado_pedido),
            ],
            States.SELECCIONANDO_PRODUCTO: [
                CallbackQueryHandler(seleccionar_producto),
                MessageHandler(filters.Regex('^🍔 Ver Menú$'), ver_menu),
            ],
            States.CANTIDAD: [
                MessageHandler(filters.TEXT, seleccionar_cantidad),
            ],
            States.OBSERVACIONES: [
                MessageHandler(filters.TEXT, agregar_observaciones),
            ],
            States.CARRITO: [
                MessageHandler(filters.TEXT, procesar_carrito),
            ],
            States.UBICACION: [
                MessageHandler(filters.LOCATION, recibir_ubicacion),
                MessageHandler(filters.Regex('^❌ Cancelar$'), lambda u, c: States.MENU),
            ],
            States.PAGO: [
                MessageHandler(filters.TEXT, procesar_pago),
            ],
        },
        fallbacks=[CommandHandler('start', start)],
    )
    
    application.add_handler(conv_handler)
    
    logger.info("🤖 Bot iniciado...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()