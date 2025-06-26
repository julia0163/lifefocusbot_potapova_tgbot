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

flask_app = Flask(__name__)
telegram_app = None

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
def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), telegram_app.bot)
        telegram_app.update_queue.put_nowait(update)
        logger.info(f"Received update: {update.update_id}")
    return "OK", 200

async def setup_application():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    webhook_url = f"https://lifefocusbot-potapova-tgbot.onrender.com/{TOKEN}"
    await application.bot.set_webhook(webhook_url)
    logger.info(f"Webhook set: {webhook_url}")
    return application

async def run_bot():
    while True:
        try:
            await telegram_app.run_polling()
        except Exception as e:
            logger.error(f"Bot error: {e}")
            await asyncio.sleep(5)

def run_flask():
    from threading import Thread
    Thread(target=lambda: asyncio.run(run_bot())).start()
    flask_app.run(host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    telegram_app = asyncio.get_event_loop().run_until_complete(setup_application())
    run_flask()
