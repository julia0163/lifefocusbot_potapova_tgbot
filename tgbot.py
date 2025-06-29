import logging
import os
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler,
    filters, ContextTypes
)

# ===== 1. НАСТРОЙКА ЛОГГИРОВАНИЯ =====
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===== 2. КОНФИГУРАЦИЯ =====
TOKEN = os.getenv("TOKEN")
CHANNEL_USERNAME = "@potapova_psy"
WEBHOOK_URL = os.getenv("https://https://lifefocusbot-potapova-tgbot.onrender.com") + "/webhook" if os.getenv("WEBHOOK_URL") else None
SECRET_TOKEN = os.getenv("SECRET_TOKEN", "default_secret_token")

# ===== 3. ОБРАБОТЧИКИ КОМАНД =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    keyboard = [
        [InlineKeyboardButton("✅ Проверить подписку", callback_data="check_sub")],
        [InlineKeyboardButton("📖 Инструкция", callback_data="show_instruction")]
    ]
    await update.message.reply_text(
        "🌟 <b>Добро пожаловать!</b>",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()
    # ... (ваш существующий код обработки кнопок)

# ===== 4. ИНИЦИАЛИЗАЦИЯ ПРИЛОЖЕНИЯ =====
application = Application.builder().token(TOKEN).build()
flask_app = Flask(__name__)

# Регистрация обработчиков
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_handler))
application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, lambda u, c: None))

# ===== 5. ВЕБХУК ЭНДПОИНТ =====
@flask_app.route('/webhook', methods=['POST'])
def webhook_handler():
    if request.headers.get('X-Telegram-Bot-Api-Secret-Token') != SECRET_TOKEN:
        return jsonify({"status": "forbidden"}), 403
    
    update = Update.de_json(request.get_json(), application.bot)
    application.process_update(update)
    return jsonify({"status": "ok"})

@flask_app.route('/')
def home():
    return "Бот работает в режиме вебхука"

# ===== 6. ЗАПУСК =====
def setup_webhook():
    """Установка вебхука при старте"""
    if WEBHOOK_URL:
        application.bot.set_webhook(
            url=WEBHOOK_URL,
            secret_token=SECRET_TOKEN
        )
        logger.info(f"Вебхук установлен на: {WEBHOOK_URL}")

if __name__ == "__main__":
    setup_webhook()
    flask_app.run(host='0.0.0.0', port=3000)
