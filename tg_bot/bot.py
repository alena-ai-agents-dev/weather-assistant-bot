import os
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from tg_bot.handlers import handle_city, city_callback, help_cmd, start_cmd, weather_cmd
from tg_bot.keyboards import popular_keyboard, language_keyboard
from tg_bot.state import set_lang
from tg_bot.texts import TEXT

from core.config import Config
BOT_TOKEN = Config.TELEGRAM_TOKEN

# Build the bot application
app = ApplicationBuilder().token(BOT_TOKEN).build()

# Register handlers
app.add_handler(CommandHandler("start", start_cmd))
app.add_handler(CommandHandler("help", help_cmd))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_city))
app.add_handler(CallbackQueryHandler(city_callback))
app.add_handler(CommandHandler("weather", weather_cmd))
