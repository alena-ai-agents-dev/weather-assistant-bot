import os
import threading
import asyncio
import time
from flask import Flask
from tg_bot.bot import app

web = Flask(__name__)

@web.route('/')
def home():
    return "Weather bot is running"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web.run(host="0.0.0.0", port=port)

async def start_bot():

    print("Starting WeatherBot...")

    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    print("Bot started successfully")

    while True:
        await asyncio.sleep(3600)

def run_bot():

    while True:

        try:

            asyncio.run(start_bot())

        except Exception as e:

            import traceback

            print("Bot crashed:")
            traceback.print_exc()

            print("Restarting in 5 seconds...")

            time.sleep(5)

if __name__ == "__main__":

    print("Starting services...")

    web_thread = threading.Thread(target=run_web)

    web_thread.daemon = True

    web_thread.start()

    run_bot()