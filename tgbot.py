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

TOKEN = os.getenv("TOKEN")
CHANNEL_USERNAME = "@potapova_psy"
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# ID чата и сообщений с практиками
SOURCE_CHAT_ID = 416561840
PRACTICE_MESSAGE_ID = 192
INSTRUCTION_MESSAGE_ID = 194

async def check_subscription(user_id: int, app) -> bool:
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
                [InlineKeyboardButton("📢 Подписаться", url="https://t.me/potapova_psy")],
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
    try:
        for i in range(1, 11):
            await context.bot.delete_message(chat_id, update.message.message_id - i)
    except Exception as e:
        logger.error(f"Ошибка удаления: {e}")
    
    await update.message.reply_text("🗑️ Последние за 48 часов сообщения бота удалены.")
    await start(update, context)

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

def main():
    # Создаем и настраиваем бота
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("clear", clear_history))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Запускаем бота с webhook
    logger.info("Запускаем бота с webhook...")
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),
        url_path=TOKEN,
        webhook_url=WEBHOOK_URL + TOKEN,
        secret_token='WEBHOOK_SECRET'
    )

if __name__ == "__main__":
    main()
