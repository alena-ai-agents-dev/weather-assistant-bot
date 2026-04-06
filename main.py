import threading
import os
from flask import Flask
from tg_bot.bot import app

web = Flask(__name__)

@web.route('/')
def home():
    return "Bot is running"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web.run(host="0.0.0.0", port=port)

def run_bot():
    app.run_polling()

if __name__ == "__main__":
    t1 = threading.Thread(target=run_bot)
    t1.start()

    run_web()