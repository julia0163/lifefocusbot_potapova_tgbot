import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import os

# Настройка логгирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация
TOKEN = os.getenv("TOKEN")
CHANNEL_USERNAME = "@potapova_psy"
PORT = int(os.getenv("PORT", 5000))

# ID чата и сообщений
SOURCE_CHAT_ID = 416561840
PRACTICE_MESSAGE_ID = 192
INSTRUCTION_MESSAGE_ID = 194

async def check_subscription(user_id: int, app) -> bool:
    try:
        member = await app.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logger.error(f"Ошибка проверки подписки: {e}")
        return False

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "check_sub":
        if await check_subscription(query.from_user.id, context.application):
            await query.message.reply_text("✅ <b>Подписка подтверждена</b>", parse_mode="HTML")
            try:
                await context.bot.copy_message(
                    chat_id=query.message.chat_id,
                    from_chat_id=SOURCE_CHAT_ID,
                    message_id=PRACTICE_MESSAGE_ID
                )
            except Exception as e:
                logger.error(f"Ошибка: {e}")
                await query.message.reply_text("❌ Ошибка загрузки", parse_mode="HTML")
        else:
            keyboard = [
                [InlineKeyboardButton("📢 Подписаться", url="https://t.me/potapova_psy")],
                [InlineKeyboardButton("✅ Я подписался", callback_data="check_sub")]
            ]
            await query.message.reply_text(
                "❌ <b>Подписка не найдена</b>",
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
            logger.error(f"Ошибка: {e}")
            await query.message.reply_text("❌ Ошибка загрузки", parse_mode="HTML")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = """🌟 <b>Добро пожаловать!</b>"""
    keyboard = [
        [InlineKeyboardButton("✅ Проверить подписку", callback_data="check_sub")],
        [InlineKeyboardButton("📖 Инструкция", callback_data="show_instruction")]
    ]
    await update.message.reply_text(
        welcome_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

def main():
    service_url = os.getenv("RENDER_EXTERNAL_URL")
    if not service_url:
        logger.error("Не удалось получить URL сервиса")
        return

    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    logger.info("Запускаем webhook...")
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=f"{service_url}/{TOKEN}",
        secret_token=os.getenv("WEBHOOK_SECRET", "default_secret")
    )

if __name__ == "__main__":
    main()
