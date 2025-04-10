
from telegram.ext import ApplicationBuilder
from handlers import setup_handlers

if __name__ == "__main__":
    app = ApplicationBuilder().token("7888544972:AAFuwZoSxvkToMX_KK7P9f95wLmQqtF39Uk").build()
    setup_handlers(app)
    app.run_polling()
