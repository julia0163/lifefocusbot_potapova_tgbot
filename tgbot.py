import logging
import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler,
    filters, ContextTypes
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

async def check_subscription(user_id: int, app: Application) -> bool:
    try:
        member = await app.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logger.error(f"Ошибка проверки подписки: {e}")
        return False

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
                await query.message.reply_text(
                    "❌ Не удалось загрузить практику. Попробуйте позже.",
                    parse_mode="HTML"
                )
        else:
            keyboard = [
                [InlineKeyboardButton("📢 Подписаться", url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}")],
                [InlineKeyboardButton("✅ Я подписался", callback_data="check_sub")]
            ]
            await query.message.reply_text(
                "❌ <b>Подписка не найдена.</b>\n\nПожалуйста, подпишитесь на канал и нажмите кнопку ниже:",
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
            await query.message.reply_text(
                "❌ Не удалось загрузить инструкцию. Попробуйте позже.",
                parse_mode="HTML"
            )

async def clear_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    message_id = update.message.message_id
    # Удаляем последние 10 сообщений бота (лучше сделать проверку на владельца)
    try:
        for i in range(10):
            await context.bot.delete_message(chat_id, message_id - i)
    except Exception as e:
        logger.warning(f"Ошибка удаления сообщений: {e}")
    await update.message.reply_text("🗑️ Последние за 48 часов сообщения бота удалены.")
    await start(update, context)

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

async def handle_any_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    message_id = update.message.message_id
    await update.message.reply_text(
        f"📌 <b>Данные этого сообщения</b>\n"
        f"chat_id: <code>{chat_id}</code>\n"
        f"message_id: <code>{message_id}</code>",
        parse_mode="HTML"
    )
    logger.info(f"Получено сообщение: chat_id={chat_id}, message_id={message_id}")

# Flask app для Render и других платформ
flask_app = Flask(__name__)

@flask_app.route('/')
def index():
    return "Bot is running"

def run_flask():
    # Включи debug=False, если продакшен
    flask_app.run(host="0.0.0.0", port=3000)

def run_bot():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("clear", clear_history))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.ALL, handle_any_message))
    logger.info("Бот успешно запущен!")
    application.run_polling()

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    run_bot()
