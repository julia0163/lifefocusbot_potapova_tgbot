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

app = Flask(__name__)
bot_app = None

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

@app.route(f'/webhook/{TOKEN}', methods=['POST'])
async def webhook():
    try:
        json_data = await request.get_json()
        update = Update.de_json(json_data, bot_app.bot)
        await bot_app.process_update(update)
        return "", 200
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return "", 500

@app.route('/health')
def health():
    return {"status": "OK", "bot_initialized": bot_app is not None}, 200

async def setup_bot():
    global bot_app
    bot_app = ApplicationBuilder().token(TOKEN).build()
    
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CallbackQueryHandler(button_handler))
    
    webhook_url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/webhook/{TOKEN}"
    await bot_app.bot.set_webhook(webhook_url, drop_pending_updates=True)
    logger.info(f"Webhook set to: {webhook_url}")

def run():
    from hypercorn.asyncio import serve
    from hypercorn.config import Config
    
    config = Config()
    config.bind = [f"0.0.0.0:{PORT}"]
    asyncio.run(serve(app, config))

if __name__ == "__main__":
    asyncio.run(setup_bot())
    run()
