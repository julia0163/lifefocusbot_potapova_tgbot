import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот успешно работает! 🚀")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    
    # Запускаем в режиме polling (без вебхуков)
    application.run_polling()

if __name__ == "__main__":
    main()  # Убрали asyncio.run для совместимости
