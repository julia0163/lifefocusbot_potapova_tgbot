from flask import Flask, request, Response
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import os

TOKEN = os.environ.get("BOT_TOKEN")  # Убедись, что переменная окружения BOT_TOKEN установлена
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"https://<твое-доменное-имя-на-render>.onrender.com{WEBHOOK_PATH}"

app = Flask(__name__)
application = Application.builder().token(TOKEN).build()


# === Команды бота ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот работает через Webhook на Render!")


application.add_handler(CommandHandler("start", start))


# === Webhook-обработчик ===
@app.route(WEBHOOK_PATH, methods=["POST"])
async def webhook() -> Response:
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), application.bot)
        await application.process_update(update)
        return Response("OK", status=200)


# === Установка webhook (один раз при запуске) ===
@app.before_first_request
def set_webhook():
    import asyncio
    asyncio.run(application.bot.set_webhook(url=WEBHOOK_URL))


# Flask-приложение для gunicorn
flask_app = app
