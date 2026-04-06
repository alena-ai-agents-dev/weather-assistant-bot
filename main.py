import os
import asyncio
import threading
from flask import Flask
from tg_bot.bot import app

# Flask health endpoint
web = Flask(__name__)

@web.route('/')
def home():
    return "Bot is running"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web.run(host="0.0.0.0", port=port)

# Run the bot properly using asyncio
async def run_bot():
    print("Starting WeatherBot...")
    await app.run_polling()  # notice the await

if __name__ == "__main__":
    # Start Flask in a thread
    t = threading.Thread(target=run_web)
    t.start()

    # Run the async bot in main thread
    asyncio.run(run_bot())