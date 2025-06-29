import os
import logging
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Переменные
TOKEN = os.getenv("TOKEN")  # Задай это в Render → Environment
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "supersecret")
APP_URL = "https://lifefocusbot-potapova-tgbot.onrender.com"

# Flask-приложение
app = Flask(__name__)
bot = Bot(token=TOKEN)
application = Application.builder().token(TOKEN).build()

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет, бот работает!")

application.add_handler(CommandHandler("start", start))

# Webhook endpoint
@app.post(f"/webhook/{WEBHOOK_SECRET}")
async def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, bot)
    await application.process_update(update)
    return "OK"

# Главная страница
@app.route("/")
def index():
    return "Бот жив!"

# Запуск
if __name__ == "__main__":
    import asyncio

    async def main():
        url = f"{APP_URL}/webhook/{WEBHOOK_SECRET}"
        await bot.set_webhook(url)
        print(f"Webhook установлен: {url}")
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))

    asyncio.run(main())
