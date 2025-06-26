import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import os
from flask import Flask, request, jsonify
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

@app.route(f'/webhook/{TOKEN}', methods=['POST'])
async def webhook():
    try:
        json_data = request.get_json(force=True)
        logger.info(f"Received update: {json_data}")
        
        update = Update.de_json(json_data, application.bot)
        await application.process_update(update)
        
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        logger.error(f"Error processing update: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/health')
def health():
    return jsonify({
        "status": "OK",
        "bot_initialized": application is not None,
        "webhook_url": f"/webhook/{TOKEN}"
    }), 200

async def setup_application():
    global application
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    webhook_url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/webhook/{TOKEN}"
    await application.bot.set_webhook(webhook_url, drop_pending_updates=True)
    logger.info(f"Webhook configured: {webhook_url}")

def run_server():
    from hypercorn.asyncio import serve
    from hypercorn.config import Config
    
    config = Config()
    config.bind = [f"0.0.0.0:{PORT}"]
    asyncio.run(serve(app, config))

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(setup_application())
    run_server()
