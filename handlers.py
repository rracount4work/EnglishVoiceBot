from telegram import ReplyKeyboardMarkup
from telegram.ext import MessageHandler, CommandHandler, filters
from logic import process_message  # универсальный обработчик

async def start(update, context):
    keyboard = [["🔊 Начать"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Нажми, чтобы начать:", reply_markup=reply_markup)

async def handle_button(update, context):
    if update.message.text == "🔊 Начать":
        await update.message.reply_text("Говори или пиши, я слушаю 🎤⌨️")

def setup_handlers(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), process_message))
    app.add_handler(MessageHandler(filters.VOICE, process_message))  # тот же обработчик
