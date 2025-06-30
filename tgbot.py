import logging
import os
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)

# Настройка логгирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация
TOKEN = os.getenv("TOKEN")
CHANNEL_USERNAME = "@potapova_psy"
SOURCE_CHAT_ID = 416561840
PRACTICE_MESSAGE_ID = 192
INSTRUCTION_MESSAGE_ID = 194
PORT = int(os.environ.get('PORT', 5000))

# Инициализация приложений
app = Flask(__name__)
application = Application.builder().token(TOKEN).build()

# [Остальные функции бота остаются без изменений...]

def setup_application():
    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, lambda u, c: None))

def run_bot():
    setup_application()
    
    if 'RENDER' in os.environ:
        # Режим для Render
        WEBHOOK_HOST = "lifefocusbot-potapova-tgbot.onrender.com"
        webhook_url = f"https://{WEBHOOK_HOST}/webhook"
        
        logger.info(f"Starting webhook on: {webhook_url}")
        
        # Установка вебхука через request
        application.updater.start_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path='TOKEN',
            webhook_url=webhook_url,
            drop_pending_updates=True
        )
    else:
        # Локальный режим
        application.run_polling()

if __name__ == '__main__':
    run_bot()
