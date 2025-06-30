import logging
import os
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)

# Настройка логгирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация
TOKEN = os.getenv("TOKEN")
CHANNEL_USERNAME = "@potapova_psy"
SOURCE_CHAT_ID = 416561840
PRACTICE_MESSAGE_ID = 192
INSTRUCTION_MESSAGE_ID = 194
PORT = int(os.environ.get('PORT', 5000))

# Инициализация приложения
app = Flask(__name__)
application = Application.builder().token(TOKEN).build()

# Функции бота
async def check_subscription(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logger.error(f"Ошибка проверки подписки: {e}")
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("✅ Проверить подписку", callback_data="check_sub")],
        [InlineKeyboardButton("📖 Инструкция", callback_data="show_instruction")]
    ]
    await update.message.reply_text(
        "Добро пожаловать!",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "check_sub":
        subscribed = await check_subscription(query.from_user.id, context)
        if subscribed:
            await context.bot.copy_message(
                chat_id=query.message.chat_id,
                from_chat_id=SOURCE_CHAT_ID,
                message_id=PRACTICE_MESSAGE_ID
            )
        else:
            keyboard = [
                [InlineKeyboardButton("📢 Подписаться", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
                [InlineKeyboardButton("✅ Проверить подписку", callback_data="check_sub")]
            ]
            await query.edit_message_text(
                "Пожалуйста, подпишитесь на канал",
                reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data == "show_instruction":
        await context.bot.copy_message(
            chat_id=query.message.chat_id,
            from_chat_id=SOURCE_CHAT_ID,
            message_id=INSTRUCTION_MESSAGE_ID
        )

# Flask роуты
@app.route('/')
def home():
    return "Бот работает!"

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == "POST":
        json_data = request.get_json()
        update = Update.de_json(json_data, application.bot)
        application.update_queue.put(update)
    return "ok"

def setup_application():
    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, lambda u, c: None))

def run_bot():
    setup_application()
    
    if 'RENDER' in os.environ:
        # Режим для Render
        WEBHOOK_HOST = "lifefocusbot-potapova-tgbot.onrender.com"
        webhook_url = f"https://{WEBHOOK_HOST}/webhook"
        
        logger.info(f"Starting webhook on: {webhook_url}")
        
        # Установка вебхука
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_url=webhook_url,
            drop_pending_updates=True
        )
    else:
        # Локальный режим
        application.run_polling()

if __name__ == '__main__':
    run_bot()
