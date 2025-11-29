import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
WEBAPP_URL = os.getenv('WEBAPP_URL', 'https://untheatric-evangeline-unprophetic.ngrok-free.dev')

# Debug
print(f"🔧 BOT_TOKEN configurado: {'✅ Sí' if BOT_TOKEN else '❌ NO'}")
print(f"🔧 WEBAPP_URL: {WEBAPP_URL}")