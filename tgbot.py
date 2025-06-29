from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "7942293176:AAGBdoQdO-EFBkI-dAjU5n8q0yvaZeOZe3g"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет!")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))

if __name__ == "__main__":
    app.run_polling()
