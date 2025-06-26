import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import os
from flask import Flask, request

# Настройка логгирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TOKEN")
PORT = int(os.getenv("PORT", 10000))

# Создаем Flask приложение для обработки вебхука
flask_app = Flask(__name__)
application = None  # Будет инициализировано в main()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    keyboard = [
        [InlineKeyboardButton("✅ Проверить", callback_data="test")]
    ]
    await update.message.reply_text(
        "🔄 Бот работает!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопок"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("✅ Всё работает корректно!")

@flask_app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    """Эндпоинт для вебхука"""
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), application.bot)
        application.update_queue.put(update)
    return "OK", 200

def main():
    global application
    
    # Инициализация бота
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Установка вебхука
    webhook_url = f"https://lifefocusbot-potapova-tgbot.onrender.com/{TOKEN}"
    application.bot.set_webhook(webhook_url)
    logger.info(f"Устанавливаем вебхук: {webhook_url}")
    
    # Запуск Flask
    flask_app.run(host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    main()
