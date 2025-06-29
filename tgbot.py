import os
import logging
import asyncio
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
import httpx

# === Конфигурация ===
TOKEN = os.getenv("BOT_TOKEN", "your_token_here")
PORT = int(os.environ.get("PORT", 10000))
BASE_URL = os.environ.get("RENDER_EXTERNAL_URL", f"http://localhost:{PORT}")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{BASE_URL}{WEBHOOK_PATH}"

# === Flask app ===
flask_app = Flask(__name__)

# === Логгирование ===
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger("tgbot")

# === Telegram обработчики ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Нажми меня", callback_data="click")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Привет! Нажми кнопку:", reply_markup=reply_markup)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Кнопка нажата!")

# === Flask Webhook ===
@flask_app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    # запускаем задачу через asyncio в фоновом режиме
    asyncio.run(application.process_update(update))
    return "ok"

# === Main ===
async def main():
    global application
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_click))

    # Устанавливаем Webhook
    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"https://api.telegram.org/bot{TOKEN}/setWebhook",
            json={"url": WEBHOOK_URL},
        )
        logger.info("Webhook установлен: %s", res.text)

    # Запускаем бота как фоновый таск
    asyncio.run(application.initialize())
    asyncio.run(application.start())

    # Flask блокирует поток, но Telegram Application работает в фоне
    flask_app.run(host="0.0.0.0", port=PORT)

    # Завершаем, если Flask вдруг остановится
    await application.stop()
    await application.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
