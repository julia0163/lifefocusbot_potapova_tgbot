import os
from telegram import Update
from telegram.ext import Application, ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("TOKEN")
RENDER_EXTERNAL_HOSTNAME = os.getenv("RENDER_EXTERNAL_HOSTNAME")
PORT = int(os.environ.get("PORT", 8443))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот успешно работает! 🚀")

def main():
    application: Application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))

    # Установка вебхука
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=f"https://{RENDER_EXTERNAL_HOSTNAME}/{BOT_TOKEN}",
    )

if __name__ == "__main__":
    main()
