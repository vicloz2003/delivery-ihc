import logging
from telegram.ext import Application, CommandHandler
from .config import BOT_TOKEN, WEBAPP_URL
from .handlers import start

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    if not BOT_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN no configurado en .env")
        print("\n🔧 Solución:")
        print("1. Crea/edita el archivo .env")
        print("2. Agrega: TELEGRAM_BOT_TOKEN=tu-token-aqui")
        print("3. Agrega: WEBAPP_URL=https://tu-ngrok-url.ngrok.io\n")
        return
    
    logger.info("🤖 Iniciando bot...")
    logger.info(f"📱 WebApp URL: {WEBAPP_URL}")
    
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    
    logger.info("✅ Bot iniciado correctamente - Esperando comandos...")
    logger.info("💡 Envía /start a tu bot en Telegram")
    
    try:
        app.run_polling(allowed_updates=['message'])
    except Exception as e:
        logger.error(f"❌ Error ejecutando el bot: {e}")

if __name__ == '__main__':
    main()