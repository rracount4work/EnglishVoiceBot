from telegram import ReplyKeyboardMarkup
from telegram.ext import MessageHandler, CommandHandler, filters
from logic import process_message


async def start(update, context):
    print("Received /start command")
    await update.message.reply_text("Привет, я твой бот!")

    keyboard = [["🔊 Start", "🗑 Reset"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Please click '🔊 Start' to start talking with me.\n"
        "Or click '🗑 Reset' to reset the dialog.\n"
        "You can speak or type in English. I will answer in English!",
        reply_markup=reply_markup
    )
    print("Sent response to /start")


async def handle_button(update, context):
    print("Received button press")

    text = update.message.text

    keyboard = [["🔊 Start", "🗑 Reset"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    if text == "🔊 Start":
        await update.message.reply_text("Speak or type your message. I'm listening 🎤⌨", reply_markup=reply_markup)

    elif text == "🗑 Reset":
        from assistant_api import reset_dialog
        reset_dialog()
        await update.message.reply_text("Dialog has been reset. Let's start a new conversation.", reply_markup=reply_markup)

    print("Sent response to button press")


def setup_handlers(app):
    print("Setting up handlers...")
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), process_message))
    app.add_handler(MessageHandler(filters.VOICE, process_message))
    print("Handlers set up successfully")
