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

TOKEN = os.getenv("TOKEN")
CHANNEL_USERNAME = "@potapova_psy"
PORT = int(os.environ.get('PORT', 10000))  # Render использует порт 10000

app = Flask(__name__)

async def check_subscription(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logger.error(f"Ошибка проверки подписки: {e}")
        return False

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        await query.answer()  # Отвечаем сразу на callback
        user_id = query.from_user.id

        if query.data == "check_sub":
            subscribed = await check_subscription(user_id, context)
            if subscribed:
                await query.message.reply_text("✅ Доступ открыт")
                await context.bot.copy_message(
                    chat_id=query.message.chat_id,
                    from_chat_id=SOURCE_CHAT_ID,
                    message_id=PRACTICE_MESSAGE_ID
                )
            else:
                keyboard = [
                    [InlineKeyboardButton("📢 Подписаться", url=f"t.me/{CHANNEL_USERNAME[1:]}")],
                    [InlineKeyboardButton("✅ Проверить подписку", callback_data="check_sub")]
                ]
                await query.message.reply_text(
                    "❌ Подписка не найдена",
                    reply_markup=InlineKeyboardMarkup(keyboard)
    except Exception as e:
        logger.error(f"Ошибка в button_handler: {e}")

@app.route('/')
def home():
    return "Бот работает!"

@app.route('/webhook', methods=['POST'])
async def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(), application.bot)
        await application.update_queue.put(update)
    return "ok"

def main():
    global application
    application = Application.builder().token(TOKEN).build()
    
    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.ALL, handle_any_message))

    # Webhook только на Render
    if 'RENDER' in os.environ:
        webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/webhook"
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_url=webhook_url,
            drop_pending_updates=True
        )
    else:
        application.run_polling()

if __name__ == '__main__':
    main()
