import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("TOKEN")
RENDER_EXTERNAL_HOSTNAME = os.getenv("RENDER_EXTERNAL_HOSTNAME")
PORT = int(os.environ.get("PORT", 8443))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот успешно работает! 🚀")

async def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))

    # Установка вебхука
    await application.bot.set_webhook(
        url=f"https://{RENDER_EXTERNAL_HOSTNAME}/{BOT_TOKEN}"
    )
    
    await application.run_polling()  # или для вебхуков: await application.start_webhook(...)

if __name__ == "__main__":
    asyncio.run(main())
