import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

    REQUEST_TIMEOUT = 10