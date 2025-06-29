from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

import os

TOKEN = os.getenv("TOKEN")  # В Render задаешь как Secret Env var

app = Flask(__name__)
application = Application.builder().token(TOKEN).build()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я живой бот!")


application.add_handler(CommandHandler("start", start))


@app.route("/", methods=["GET"])
def index():
    return "Bot is running!"


@app.route(f"/webhook/{TOKEN}", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return "OK", 200


if __name__ == "__main__":
    import asyncio

    async def run():
        await application.initialize()
        await application.start()
        await application.updater.start_webhook(
            listen="0.0.0.0",
            port=int(os.environ.get("PORT", 3000)),
            url_path=f"webhook/{TOKEN}",
            webhook_url=f"https://{os.environ['RENDER_EXTERNAL_HOSTNAME']}/webhook/{TOKEN}",
        )
        await application.updater.idle()

    asyncio.run(run())
