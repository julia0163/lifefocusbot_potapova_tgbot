from flask import Flask, request
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

app = Flask(__name__)
application = Application.builder().token(os.getenv("TOKEN")).build()

@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(), application.bot)
    application.update_queue.put(update)
    return "ok"

def main():
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    if 'RENDER' in os.environ:
        application.run_webhook(
            listen="0.0.0.0",
            port=5000,
            webhook_url="https://lifefocusbot-potapova-tgbot.onrender.com/webhook",
            drop_pending_updates=True
        )
    else:
        application.run_polling()

if __name__ == '__main__':
    main()
