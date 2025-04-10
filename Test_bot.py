import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.error import TimedOut, NetworkError

# Загружаем токен из .env файла
load_dotenv(".env")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("Бот работает! Привет 👋")
    except (TimedOut, NetworkError):
        print("❌ Сеть перегружена или Telegram недоступен.")
        # Пытаемся сообщить пользователю
        try:
            await update.message.reply_text(
                "Кажется, проблема с интернетом. Попробуйте позже."
            )
        except Exception:
            pass  # Если и это не удаётся — просто молчим

# Запуск бота
if __name__ == "__main__":
    try:
        app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        print("✅ Бот запущен.")
        app.run_polling()
    except Exception as e:
        print("🚫 Ошибка запуска:", str(e))
        print("Проверь соединение с интернетом и токен.")
