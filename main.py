from tg_bot.bot import app  # use same variable name as bot.py

if __name__ == "__main__":
    print("Starting WeatherBot...")
    app.run_polling()