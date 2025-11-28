# ============================================
# bot/handlers.py
# ============================================
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ContextTypes
from .config import WEBAPP_URL

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start - Abre la Mini App"""
    user = update.effective_user
    
    text = (
        f"👋 ¡Hola {user.first_name}!\n\n"
        f"Bienvenido a **DeliveryIhc** 🍕🚀\n\n"
        f"Presiona el botón para abrir el menú:"
    )
    
    keyboard = [[
        InlineKeyboardButton("🍔 Abrir Menú", web_app=WebAppInfo(url=WEBAPP_URL))
    ]]
    
    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )