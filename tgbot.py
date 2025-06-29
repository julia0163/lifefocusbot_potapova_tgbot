import logging
import asyncio
from flask import Flask, request, abort
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
import os
import httpx

# === Настройки ===
TOKEN = os.getenv("BOT_TOKEN", "your_token_here")
WEBHOOK_PATH = "/webhook"
PORT = int(os.environ.get("PORT", 10000))
BASE_URL = os.environ.get("RENDER_EXTERNAL_URL", f"http://localhost:{PORT}")
WEBHOOK_URL = f"{BASE_URL}{WEBHOOK_PATH}"

# === Логгирование ===
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# === Flask ===
flask_app = Flask(__name__)

# === Обработчики ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Нажми меня", callback_data="button_click")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Привет! Нажми на кнопку:", reply_markup=reply_markup)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="Кнопка нажата!")

# === Flask Webhook ===
@flask_app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), application.bot)
        # запускаем задачу внутри event loop бота
        asyncio.run_coroutine_threadsafe(
            application.process_update(update), application.loop
        )
        return "OK"
    else:
        abort(403)

# === Main ===
async def main():
    global application
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_click))

    # Установка Webhook
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://api.telegram.org/bot{TOKEN}/setWebhook",
            json={"url": WEBHOOK_URL},
        )
        logger.info("Webhook установлен: %s", response.text)

    # Запуск Flask
    flask_app.run(host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    try:
        # Создаем event loop вручную для Flask + Telegram Application
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped.")
