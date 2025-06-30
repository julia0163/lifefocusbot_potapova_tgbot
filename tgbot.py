import asyncio
from flask import Flask, request

app = Flask(__name__)

# ... (остальные импорты и настройки остаются без изменений)

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == "POST":
        json_data = request.get_json()
        update = Update.de_json(json_data, application.bot)
        
        # Запускаем обработку обновления в event loop
        asyncio.run_coroutine_threadsafe(
            application.process_update(update),
            application.updater.bot.application.create_task
        )
    return "ok"

def run_flask():
    app.run(host='0.0.0.0', port=PORT)

def main():
    # Регистрация обработчиков (как было ранее)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, lambda u, c: None))

    if 'RENDER' in os.environ:
        # Запускаем Flask в основном потоке
        run_flask()
    else:
        application.run_polling()

if __name__ == '__main__':
    main()
