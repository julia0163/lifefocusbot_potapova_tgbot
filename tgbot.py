import asyncio
from aiohttp import web
from telegram.ext import Application, CommandHandler

TOKEN = '7942293176:AAGBdoQdO-EFBkI-dAjU5n8q0yvaZeOZe3g'

async def start(update, context):
    await update.message.reply_text('Бот запущен!')

# Бот
application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))

# Фейковый веб-сервер для Render
async def handle(request):
    return web.Response(text="Bot is running!")

async def main():
    # Запуск бота
    asyncio.create_task(application.run_polling())
    
    # Запуск aiohttp сервера
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()

    # Получаем порт от Render (обязательно!)
    import os
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    print(f"Server started on port {port}")
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
