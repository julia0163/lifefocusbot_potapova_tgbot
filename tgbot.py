import logging
import os
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler,
    ContextTypes, filters
)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Константы
TOKEN = os.getenv("TOKEN")  # или напрямую вставь токен сюда
CHANNEL_USERNAME = "@potapova_psy"

SOURCE_CHAT_ID = 416561840
PRACTICE_MESSAGE_ID = 192
INSTRUCTION_MESSAGE_ID = 194

# Flask-приложение
flask_app = Flask(__name__)
application = Application.builder().token(TOKEN).build()

@flask_app.route('/')
def index():
    return "Бот работает!"

@flask_app.route('/webhook', methods=['POST'])
async def webhook():
    if request.method == "POST":
        await application.update_queue.put(Update.de_json(request.get_json(force=True), application.bot))
    return "ok"

# Проверка подписки
async def check_subscription(user_id: int, app: Application) -> bool:
    try:
        member = await app.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logger.error(f"Ошибка проверки подписки: {e}")
        return False

# Обработка кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "check_sub":
        subscribed = await check_subscription(user_id, context.application)
        if subscribed:
            await query.message.reply_text(
                "✅ <b>Подписка подтверждена. Доступ к практике открыт</b>",
                parse_mode="HTML"
            )
            try:
                await context.bot.copy_message(
                    chat_id=query.message.chat_id,
                    from_chat_id=SOURCE_CHAT_ID,
                    message_id=PRACTICE_MESSAGE_ID
                )
            except Exception as e:
                logger.error(f"Ошибка пересылки практики: {e}")
                await query.message.reply_text("❌ Не удалось загрузить практику.")
        else:
            keyboard = [
                [InlineKeyboardButton("📢 Подписаться", url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}")],
                [InlineKeyboardButton("✅ Я подписался", callback_data="check_sub")]
            ]
            await query.message.reply_text(
                "❌ <b>Подписка не найдена.</b>\n\nПожалуйста, подпишитесь и нажмите кнопку ниже:",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="HTML"
            )

    elif query.data == "show_instruction":
        try:
            await context.bot.copy_message(
                chat_id=query.message.chat_id,
                from_chat_id=SOURCE_CHAT_ID,
                message_id=INSTRUCTION_MESSAGE_ID
            )
        except Exception as e:
            logger.error(f"Ошибка пересылки инструкции: {e}")
            await query.message.reply_text("❌ Не удалось загрузить инструкцию.")

# Команды
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🌟 <b>Добро пожаловать в пространство практик для ЖИЗНИ 🌿</b>\n\n"
        "🧠 Доступна практика <b>«Вторичные выгоды»</b>\n"
        "🎧 Аудио будет доступно после подписки на канал."
    )
    keyboard = [
        [InlineKeyboardButton("✅ Проверить подписку", callback_data="check_sub")],
        [InlineKeyboardButton("📖 Инструкция", callback_data="show_instruction")]
    ]
    await update.message.reply_text(
        welcome_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

async def clear_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    message_id = update.message.message_id
    try:
        for i in range(10):
            await context.bot.delete_message(chat_id, message_id - i)
    except Exception as e:
        logger.warning(f"Ошибка удаления сообщений: {e}")
    await update.message.reply_text("🗑️ Сообщения очищены.")
    await start(update, context)

async def handle_any_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    message_id = update.message.message_id
    await update.message.reply_text(
        f"chat_id: <code>{chat_id}</code>\nmessage_id: <code>{message_id}</code>",
        parse_mode="HTML"
    )

# Регистрация хендлеров
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("clear", clear_history))
application.add_handler(CallbackQueryHandler(button_handler))
application.add_handler(MessageHandler(filters.ALL, handle_any_message))

# Запуск бота (установим webhook)
async def set_webhook():
    url = os.getenv("https://lifefocusbot-potapova-tgbot.onrender.com") + "/webhook"
    await application.bot.set_webhook(url)

if __name__ == "__main__":
    import asyncio
    asyncio.run(set_webhook())
    application.run_webhook(
        listen="0.0.0.0",
        port=3000,
        webhook_url=os.getenv("https://lifefocusbot-potapova-tgbot.onrender.com/") + "/webhook"
    )
