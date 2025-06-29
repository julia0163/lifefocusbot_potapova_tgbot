import os
import logging
import threading
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler,
    ContextTypes, filters
)

# --- Настройка логов ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Конфигурация ---
TOKEN = os.getenv("TOKEN")
CHANNEL_USERNAME = "@potapova_psy"
SOURCE_CHAT_ID = 416561840
PRACTICE_MESSAGE_ID = 192
INSTRUCTION_MESSAGE_ID = 194

# --- Flask-приложение ---
flask_app = Flask(__name__)
app: Application = None  # Инициализируем позже


# --- Проверка подписки ---
async def check_subscription(user_id: int, app_instance: Application) -> bool:
    try:
        member = await app_instance.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logger.error(f"Ошибка при проверке подписки: {e}")
        return False


# --- Обработка кнопок ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "check_sub":
        if await check_subscription(user_id, context.application):
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
                logger.error(f"Ошибка отправки практики: {e}")
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
            logger.error(f"Ошибка отправки инструкции: {e}")
            await query.message.reply_text("❌ Не удалось загрузить инструкцию.")


# --- Команды ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = (
        "🌟 <b>Добро пожаловать в пространство практик для ЖИЗНИ 🌿</b>\n\n"
        "Здесь вы найдете инструменты для работы с:\n"
        "• Гневом и раздражением\n"
        "• Тревогой и беспокойством\n"
        "• Апатией и усталостью\n\n"
        "<b>Сейчас доступна:</b>\n"
        "🧠 Практика <b>«Вторичные выгоды»</b>\n\n"
        "🎧 <b>Аудио-практики доступны после подписки на канал</b>"
    )
    keyboard = [
        [InlineKeyboardButton("✅ Проверить подписку", callback_data="check_sub")],
        [InlineKeyboardButton("📖 Инструкция", callback_data="show_instruction")]
    ]
    await update.message.reply_text(
        welcome,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )


async def clear_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    try:
        for i in range(10):
            await context.bot.delete_message(chat_id, update.message.message_id - i)
    except Exception as e:
        logger.warning(f"Ошибка при удалении сообщений: {e}")
    await update.message.reply_text("🗑️ История очищена.")
    await start(update, context)


async def handle_any_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    message_id = update.message.message_id
    logger.info(f"Получено сообщение: chat_id={chat_id}, message_id={message_id}")
    await update.message.reply_text(
        f"📌 <b>chat_id:</b> <code>{chat_id}</code>\n"
        f"<b>message_id:</b> <code>{message_id}</code>",
        parse_mode="HTML"
    )


# --- Webhook маршрут ---
@flask_app.route("/webhook", methods=["POST"])
def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), app.bot)
        app.update_queue.put(update)
    return "ok"


@flask_app.route("/")
def index():
    return "Bot is running"


# --- Запуск приложения ---
def run():
    global app
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear_history))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.ALL, handle_any_message))

    # Устанавливаем Webhook URL
    webhook_url = f"https://lifefocusbot-potapova-tgbot.onrender.com/webhook"
    app.run_webhook(
        listen="0.0.0.0",
        port=3000,
        webhook_url=webhook_url
    )


if __name__ == "__main__":
    threading.Thread(target=lambda: flask_app.run(host="0.0.0.0", port=3000), daemon=True).start()
    run()
