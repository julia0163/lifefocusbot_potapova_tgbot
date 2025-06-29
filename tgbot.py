import logging
import asyncio
import os

from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Настройка логов
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получение токена и webhook пути

TOKEN = "7942293176:AAGBdoQdO-EFBkI-dAjU5n8q0yvaZeOZe3g"
WEBHOOK_HOST = "https://lifefocusbot-potapova-tgbot.onrender.com"
WEBHOOK_PATH = f"/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
# Flask app
app = Flask(__name__)

# Инициализация Telegram приложения
application = Application.builder().token(BOT_TOKEN).build()

# Глобальный event loop
loop = asyncio.get_event_loop()

# Пример команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Бот работает 🎉")

# Обработчик команды
application.add_handler(CommandHandler("start", start))

# Webhook обработчик
@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    loop.create_task(application.process_update(update))
    return "ok"

# Установка Webhook и запуск Flask
async def set_webhook():
    await application.bot.set_webhook(WEBHOOK_URL)
    logger.info("Webhook установлен: %s", WEBHOOK_URL)

if __name__ == "__main__":
    loop.run_until_complete(set_webhook())  # Устанавливаем Webhook
    app.run(host="0.0.0.0", port=10000)     # Запускаем Flask
