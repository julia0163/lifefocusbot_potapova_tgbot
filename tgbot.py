import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import os
from flask import Flask, request
import asyncio

# Настройка логгирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TOKEN")
PORT = int(os.getenv("PORT", 10000))

# Инициализация Flask
flask_app = Flask(__name__)

# Глобальная переменная для приложения Telegram
application = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("✅ Проверить", callback_data="test")]]
    await update.message.reply_text(
        "🔄 Бот работает!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("✅ Всё работает корректно!")

@flask_app.route(f'/{TOKEN}', methods=['POST'])
async def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), application.bot)
        await application.update_queue.put(update)
    return "OK", 200

async def main():
    global application
    
    # Инициализация приложения Telegram
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Установка вебхука
    webhook_url = f"https://lifefocusbot-potapova-tgbot.onrender.com/{TOKEN}"
    await application.bot.set_webhook(webhook_url)
    logger.info(f"Вебхук установлен: {webhook_url}")
    
    # Запуск Flask в асинхронном режиме
    from hypercorn.asyncio import serve
    from hypercorn.config import Config
    
    config = Config()
    config.bind = [f"0.0.0.0:{PORT}"]
    await serve(flask_app, config)

if __name__ == "__main__":
    # Запуск асинхронного приложения
    asyncio.run(main())
