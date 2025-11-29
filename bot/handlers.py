from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ContextTypes
from .config import WEBAPP_URL

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start - Abre la Mini App"""
    user = update.effective_user
    
    print(f"📱 /start recibido de: {user.first_name} (ID: {user.id})")
    
    text = (
        f"👋 ¡Hola {user.first_name}!\n\n"
        f"Bienvenido a **DeliveryIhc** 🍕🚀\n\n"
        f"Presiona el botón para abrir el menú:"
    )
    
    keyboard = [[
        InlineKeyboardButton(
            "🍔 Abrir Menú", 
            web_app=WebAppInfo(url=WEBAPP_URL)
        )
    ]]
    
    try:
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        print(f"✅ Mensaje enviado correctamente a {user.first_name}")
    except Exception as e:
        print(f"❌ Error enviando mensaje: {e}")