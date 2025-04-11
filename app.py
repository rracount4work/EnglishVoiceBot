import os
import traceback
import asyncio
import threading
from flask import Flask, request
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application
from handlers import setup_handlers
from logger import logging

# Загрузка конфигурации
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("Token not found. Set TELEGRAM_TOKEN in .env")

# Инициализация Flask и Telegram
app_flask = Flask(__name__)
application = Application.builder().token(TELEGRAM_TOKEN).build()

# Создаем цикл событий
loop = asyncio.new_event_loop()


# Функция для запуска цикла событий в отдельном потоке
def run_loop():
    asyncio.set_event_loop(loop)
    loop.run_forever()


# Запускаем цикл событий в отдельном потоке
thread = threading.Thread(target=run_loop, daemon=True)
thread.start()


# Асинхронная функция для обработки вебхука
async def process_webhook(update_json):
    try:
        print("Parsing update...")
        logging.info("Parsing update...")
        update = Update.de_json(update_json, application.bot)
        if update:
            print(f"Update parsed: {update}")
            logging.info(f"Update parsed: {update}")
            print("Processing update...")
            logging.info("Processing update...")
            await application.process_update(update)
            print("Update processed successfully")
            logging.info("Update processed successfully")
        else:
            print("Failed to parse update")
            logging.error("Failed to parse update")
    except Exception as e:
        print(f"Error in process_webhook: {e}")
        print(traceback.format_exc())
        logging.error(f"Error in process_webhook: {e}\n{traceback.format_exc()}")


# Flask эндпоинт для вебхука
@app_flask.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def webhook():
    try:
        print("Received webhook update")
        logging.info("Received webhook update")
        update_json = request.get_json()
        if update_json:
            print(f"Webhook JSON: {update_json}")
            logging.info(f"Webhook JSON: {update_json}")
            # Запускаем асинхронную обработку в цикле событий
            asyncio.run_coroutine_threadsafe(process_webhook(update_json), loop)
        else:
            print("No JSON data in webhook request")
            logging.error("No JSON data in webhook request")
    except Exception as e:
        print(f"Error in webhook: {e}")
        print(traceback.format_exc())
        logging.error(f"Error in webhook: {e}\n{traceback.format_exc()}")
        return '', 500
    return '', 200


@app_flask.route('/')
def home():
    print("Received request to /")
    logging.info("Received request to /")
    return 'Hello, Flask is running!'


# Инициализация вебхука
async def init_webhook():
    ngrok_url = 'https://e063-156-202-138-143.ngrok-free.app/'  # Обнови на свой URL
    webhook_url = f'{ngrok_url}{TELEGRAM_TOKEN}'
    print(f"Setting webhook to: {webhook_url}")
    logging.info(f"Setting webhook to: {webhook_url}")
    await application.bot.set_webhook(webhook_url)
    print(f"Webhook установлен на: {webhook_url}")
    logging.info(f"Webhook set to: {webhook_url}")


# Запуск бота
if __name__ == '__main__':
    print("Starting bot...")
    logging.info("Starting bot...")

    # Инициализируем Application в уже запущенном цикле
    asyncio.run_coroutine_threadsafe(application.initialize(), loop).result()
    print("Application initialized")
    logging.info("Application initialized")

    asyncio.run_coroutine_threadsafe(application.start(), loop).result()
    print("Application started")
    logging.info("Application started")

    # Настраиваем обработчики после инициализации
    setup_handlers(application)

    asyncio.run_coroutine_threadsafe(init_webhook(), loop).result()
    print("Webhook setup completed")
    logging.info("Webhook setup completed")

    try:
        app_flask.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
    finally:
        # Останавливаем Application при завершении
        asyncio.run_coroutine_threadsafe(application.stop(), loop).result()
        loop.call_soon_threadsafe(loop.stop)
        thread.join()
        loop.close()
        print("Application stopped and loop closed")
        logging.info("Application stopped and loop closed")