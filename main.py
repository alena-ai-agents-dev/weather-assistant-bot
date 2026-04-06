import os
import threading
from flask import Flask
from tg_bot.bot import app
import asyncio

# Flask health endpoint
web = Flask(__name__)

@web.route('/')
def home():
    return "Bot is running"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web.run(host="0.0.0.0", port=port)

# Run the bot in a thread using asyncio
def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(app.run_polling())

if __name__ == "__main__":
    # Start Flask in a thread (Render health check)
    t = threading.Thread(target=run_web)
    t.start()

    # Start Telegram bot
    run_bot()