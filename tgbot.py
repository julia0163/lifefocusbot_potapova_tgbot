import logging
import os
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler,
    filters, ContextTypes
)

# Настройка логгирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TOKEN")
CHANNEL_USERNAME = "@potapova_psy"
WEBHOOK_URL = "https://https://lifefocusbot-potapova-tgbot.onrender.com/webhook"  # Замените на ваш URL
SECRET_TOKEN = "your_secret_key"  # Сгенерируйте сложный ключ

# Инициализация приложения
application = Application.builder().token(TOKEN).build()
flask_app = Flask(__name__)

# Ваши обработчики (start, button_handler и др.) остаются без изменений
# ...

# Регистрация обработчиков
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_handler))
application.add_handler(MessageHandler(filters.ALL, handle_any_message))

# Вебхук-эндпоинт
@flask_app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('X-Telegram-Bot-Api-Secret-Token') != SECRET_TOKEN:
        return jsonify({"status": "forbidden"}), 403
    
    update = Update.de_json(request.get_json(), application.bot)
    application.process_update(update)
    return jsonify({"status": "ok"})

@flask_app.route('/')
def index():
    return "Bot is running in webhook mode"

def main():
    # Установка вебхука
    application.bot.set_webhook(
        url=WEBHOOK_URL,
        secret_token=SECRET_TOKEN
    )
    logger.info("Webhook установлен на: %s", WEBHOOK_URL)

# В конце файла замените на:
if __name__ == "__main__":
    # Для локального тестирования (раскомментируйте если нужно)
    # application.run_polling()
    
    # Для продакшена на Render
    application.bot.set_webhook(
        url=WEBHOOK_URL,
        secret_token=SECRET_TOKEN
    )
    flask_app.run(host='0.0.0.0', port=3000)
