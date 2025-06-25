import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import os

# Настройка логгирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TOKEN")
CHANNEL_USERNAME = "@potapova_psy"

# ID чата и сообщений с практиками
SOURCE_CHAT_ID = 416561840  # ID чата, где хранятся медиафайлы
PRACTICE_MESSAGE_ID = 192    # ID голосового сообщения с практикой
INSTRUCTION_MESSAGE_ID = 194 # ID видео с инструкцией

async def check_subscription(user_id: int, app) -> bool:
    """Проверка подписки на канал"""
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
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()

    if query.data == "check_sub":
        if await check_subscription(query.from_user.id, context.application):
            await query.message.reply_text(
                "✅ <b>Подписка подтверждена. Доступ к практике открыт</b>",
                parse_mode="HTML"
            )
            
            # Пересылаем голосовое с практикой
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
        # Пересылаем видео с инструкцией
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
    """Очистка истории сообщений"""
    chat_id = update.effective_chat.id
    try:
        # Удаляем последние 10 сообщений бота
        for i in range(1, 11):
            await context.bot.delete_message(chat_id, update.message.message_id - i)
    except Exception as e:
        logger.error(f"Ошибка удаления: {e}")
    
    await update.message.reply_text("🗑️ Последние за 48 часов сообщения бота удалены.")
    await start(update, context)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Стартовое сообщение с улучшенным текстом"""
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

async def handle_any_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ловим любое сообщение и выводим chat_id и message_id"""
    chat_id = update.effective_chat.id
    message_id = update.message.message_id

    await update.message.reply_text(
        f"📌 <b>Данные этого сообщения</b>\n"
        f"chat_id: <code>{chat_id}</code>\n"
        f"message_id: <code>{message_id}</code>",
        parse_mode="HTML"
    )

    logger.info(f"Получено сообщение: chat_id={chat_id}, message_id={message_id}")

if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear_history))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.ALL, handle_any_message))

    logger.info("Бот успешно запущен!")
    app.run_polling()
