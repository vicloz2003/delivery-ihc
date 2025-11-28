import logging
from telegram.ext import Application, CommandHandler
from .config import BOT_TOKEN
from .handlers import start

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    if not BOT_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN no configurado")
        return
    
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    
    logger.info("🤖 Bot iniciado - Mini App Mode")
    app.run_polling()

if __name__ == '__main__':
    main()