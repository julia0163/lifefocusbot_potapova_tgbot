import logging
import os
import threading
import asyncio

from flask import Flask, request, abort
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)

# Настройка логов
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Переменные окружения и настройки
TOKEN = os.getenv("TOKEN")
CHANNEL_USERNAME = "@potapova_psy"

SOURCE_CHAT_ID = 416561840
PRACTICE_MESSAGE_ID = 192
INSTRUCTION_MESSAGE_ID = 194

PORT = int(os.environ.get("PORT", 3000))
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"https://lifefocusbot-potapova-tgbot.onrender.com{WEBHOOK_PATH}"

# Flask-приложение
flask_app = Flask(__name__)

# Создаём Telegram-приложение
application = Application.builder().token(TOKEN).build()


# ========= ЛОГИКА БОТА =========

async def check_subscription(user_id: int, app: Application) -> bool:
    try:
        member = await app.bot.get_chat_member(
            chat_id=CHANNEL_USERNAME,
            user_id=user_id
        )
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logger.error(f"Ошибка проверки подписки: {e}")
        return False


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "check_sub":
        if await check_subscription(query.from_user.id, context.application):
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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = """
🌟 <b>Добро пожаловать в пространство практик для ЖИЗНИ 🌿</b>

Здесь вы найдете инструменты для работы с разными состояниями:
• Гневом и раздражением
• Тревогой и беспокойством
• Апатией и усталостью

<b>Сейчас доступна:</b>
🧠 Практика <b>«Вторичные выгоды»</b> - помогает разорвать связь между скрытыми преимуществами и вашим негативным состоянием.
"""

    keyboard = [
        [InlineKeyboardButton("✅ Проверить подписку", callback_data="check_sub")],
        [InlineKeyboardButton("📖 Инструкция", callback_data="show_instruction")]
    ]
    await update.message.reply_text(
        welcome_text + "\n\n🎧 <b>Аудио-практики доступны после подписки на канал</b>",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )


async def clear_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    try:
        for i in range(1, 11):
            await context.bot.delete_message(chat_id, update.message.message_id - i)
    except Exception as e:
        logger.error(f"Ошибка удаления сообщений: {e}")
    await update.message.reply_text("🗑️ Последние за 48 часов сообщения бота удалены.")
    await start(update, context)


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


# ========== FLASK HANDLERS ==========

@flask_app.route("/")
def index():
    return "Bot is running!"


@flask_app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), application.bot)
        asyncio.create_task(application.process_update(update))
        return "OK"
    else:
        abort(403)


# ========== ЗАПУСК ==========
def start_flask():
    flask_app.run(host="0.0.0.0", port=PORT)


async def set_webhook():
    await application.bot.set_webhook(WEBHOOK_URL)
    logger.info("Webhook установлен")


async def main():
    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("clear", clear_history))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.ALL, handle_any_message))

    await application.initialize()
    await set_webhook()
    await application.start()
    logger.info("Telegram application запущен")


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    threading.Thread(target=start_flask).start()
    loop.run_until_complete(main())
