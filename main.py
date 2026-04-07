import os
import threading
import asyncio
from flask import Flask
from tg_bot.bot import app

web = Flask(__name__)

@web.route('/')
def home():
    return "Bot is running"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web.run(host="0.0.0.0", port=port)

async def start_bot():
    print("Starting WeatherBot...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    while True:
        await asyncio.sleep(3600)

def run_bot():
    asyncio.run(start_bot())

if __name__ == "__main__":
    t = threading.Thread(target=run_web)
    t.start()

    run_bot()