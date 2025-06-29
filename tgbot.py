import logging
import os
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, ContextTypes
)
import asyncio
import httpx

TOKEN = "7942293176:AAGBdoQdO-EFBkI-dAjU5n8q0yvaZeOZe3g"
WEBHOOK_HOST = "https://lifefocusbot-potapova-tgbot.onrender.com"
WEBHOOK_PATH = f"/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

application = Application.builder().token(TOKEN).build()

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Нажми меня", callback_data="button_click")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Привет! Нажми кнопку ниже.", reply_markup=reply_markup)

# Обработка кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Ты нажал кнопку!")

application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_handler))


@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    asyncio.run(application.process_update(update))
    return "ok"


@app.route("/", methods=["GET"])
def index():
    return "OK", 200


async def set_webhook():
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"https://api.telegram.org/bot{TOKEN}/setWebhook",
            json={"url": WEBHOOK_URL}
        )
        logger.info("Webhook установлен: %s", r.text)

async def main():
    await application.initialize()
    await set_webhook()
    logger.info("Запуск Flask-сервера...")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))


if __name__ == "__main__":
    asyncio.run(main())
