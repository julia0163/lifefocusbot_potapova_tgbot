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

@flask_app.route(f'/{TOKEN}', methods=['POST'])
async def webhook():
    """Эндпоинт для вебхука"""
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), bot)
        await application.process_update(update)
    return "OK", 200

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

def main():
    global bot, application
    
    # Инициализация бота
    application = ApplicationBuilder().token(TOKEN).build()
    bot = application.bot
    
    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Установка вебхука
    webhook_url = f"https://lifefocusbot-potapova-tgbot.onrender.com/{TOKEN}"
    logger.info(f"Устанавливаем вебхук: {webhook_url}")
    
    # Запуск Flask
    if __name__ == "__main__":
        flask_app.run(host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    main()
