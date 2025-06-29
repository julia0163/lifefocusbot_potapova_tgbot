import logging
import os
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    ContextTypes, MessageHandler, filters
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TOKEN")
CHANNEL_USERNAME = "@potapova_psy"
PORT = int(os.environ.get('PORT', 10000))  # Render использует порт 10000

app = Flask(__name__)

# Ваши обработчики (start, button_handler и т.д.) остаются без изменений

@app.route('/')
def home():
    return "Бот работает!"

@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), app.bot)
    app.dispatcher.process_update(update)
    return 'ok'

def main():
    application = Application.builder().token(TOKEN).build()
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.ALL, handle_any_message))

    # Настройка webhook только в production
    if os.environ.get('RENDER'):
        webhook_url = f"https://{os.environ.get('https://https://lifefocusbot-potapova-tgbot.onrender.com')}/webhook"
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_url=webhook_url
        )
    else:
        application.run_polling()  # Для локального тестирования

if __name__ == '__main__':
    main()
