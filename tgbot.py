import os
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("TOKEN")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "secret123")  # можно любое слово
APP_URL = os.getenv("https://lifefocusbot-potapova-tgbot.onrender.com")  # https://your-render-url.onrender.com

app = Flask(__name__)
bot = Bot(token=TOKEN)
application = Application.builder().token(TOKEN).build()

# Простая команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Бот работает 🤖")

application.add_handler(CommandHandler("start", start))

@app.route(f"/webhook/{WEBHOOK_SECRET}", methods=["POST"])
async def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, bot)
    await application.process_update(update)
    return "ok"

@app.route("/", methods=["GET"])
def index():
    return "Бот запущен!"

if __name__ == "__main__":
    import asyncio

    async def set_webhook():
        await bot.set_webhook(f"{APP_URL}/webhook/{WEBHOOK_SECRET}")

    asyncio.run(set_webhook())
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))
