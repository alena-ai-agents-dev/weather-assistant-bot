import logging
from logging.handlers import RotatingFileHandler

# -----------------------
# Logging Setup
# -----------------------

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Rotating file handler
file_handler = RotatingFileHandler(
    "bot.log",       # Log file name
    maxBytes=5*1024*1024,  # 5 MB per file
    backupCount=2    # Keep 2 old files
)
file_handler.setFormatter(
    logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
)
logger.addHandler(file_handler)

# Optional: also log to console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(
    logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
)
logger.addHandler(console_handler)

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

    logger.info("Starting WeatherBot...")

    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    logger.info("Bot started successfully")

    while True:
        await asyncio.sleep(3600)

def run_bot():

    while True:

        try:

            asyncio.run(start_bot())

        except Exception:


            logger.error("Bot crashed:")
            logger.exception("Exception occurred")

            logger.info("Restarting in 5 seconds...")

            time.sleep(5)

if __name__ == "__main__":

    logger.info("Starting services...")

    web_thread = threading.Thread(target=run_web)

    web_thread.daemon = True

    web_thread.start()

    run_bot()