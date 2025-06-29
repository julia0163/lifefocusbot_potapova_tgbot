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
SOURCE_CHAT_ID = 416561840
PRACTICE_MESSAGE_ID = 192
INSTRUCTION_MESSAGE_ID = 194
PORT = int(os.environ.get('PORT', 10000))  # Render использует порт 10000

app = Flask(__name__)

async def check_subscription(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logger.error(f"Ошибка проверки подписки: {e}")
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🌟 <b>Добро пожаловать в пространство практик для ЖИЗНИ 🌿</b>\n\n"
        "Здесь вы найдете инструменты для работы с разными состояниями:\n"
        "• Гневом и раздражением\n"
        "• Тревогой и беспокойством\n"
        "• Апатией и усталостью\n\n"
        "<b>Сейчас доступна:</b>\n"
        "🧠 Практика <b>«Вторичные выгоды»</b> - помогает разорвать связь между скрытыми преимуществами и вашим негативным состоянием."
    )
    keyboard = [
        [InlineKeyboardButton("✅ Проверить подписку", callback_data="check_sub")],
        [InlineKeyboardButton("📖 Инструкция", callback_data="show_instruction")]
    ]
    await update.message.reply_text(
        welcome_text + "\n\n🎧 <b>Аудио-практики доступны после подписки на канал</b>",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        await query.answer()  # Отвечаем сразу на callback
        user_id = query.from_user.id

        if query.data == "check_sub":
            subscribed = await check_subscription(user_id, context)
            if subscribed:
                await query.message.reply_text("✅ <b>Подписка подтверждена. Доступ к практике открыт</b>", parse_mode="HTML")
                await context.bot.copy_message(
                    chat_id=query.message.chat_id,
                    from_chat_id=SOURCE_CHAT_ID,
                    message_id=PRACTICE_MESSAGE_ID
                )
            else:
                keyboard = [
                    [InlineKeyboardButton("📢 Подписаться", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
                    [InlineKeyboardButton("✅ Я подписался", callback_data="check_sub")]
                ]
                await query.message.reply_text(
                    "❌ <b>Подписка не найдена.</b>\n\nПожалуйста, подпишитесь на канал и нажмите кнопку ниже:",
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode="HTML"
                )
        
        elif query.data == "show_instruction":
            await context.bot.copy_message(
                chat_id=query.message.chat_id,
                from_chat_id=SOURCE_CHAT_ID,
                message_id=INSTRUCTION_MESSAGE_ID
            )
    except Exception as e:
        logger.error(f"Ошибка в button_handler: {e}")

async def handle_any_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Пожалуйста, используйте кнопки меню или команду /start")

@app.route('/')
def home():
    return "Бот работает!"

@app.route('/webhook', methods=['POST'])
async def webhook():
    if request.method == "POST":
        json_data = request.get_json()
        update = Update.de_json(json_data, application.bot)
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
