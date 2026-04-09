import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from core.weather_service import WeatherService
from tg_bot.keyboards import popular_keyboard, cities_keyboard, language_keyboard
from core.constants import POPULAR_CITIES
from tg_bot.texts import TEXT
from tg_bot.state import get_lang, set_lang, set_cities, get_cities, set_state, get_state, clear_state
from deep_translator import GoogleTranslator
from tg_bot.utils import get_country_name
from tg_bot.utils import weather_emoji, country_flag
from core.errors import CityNotFound, NetworkError, TimeoutError, APIError

service = WeatherService()



def translate_city_to_english(city_name):
    try:
        return GoogleTranslator(source='auto', target='en').translate(city_name)
    except Exception:
        return city_name

def normalize(text):
    return text.lower().strip()

def city_score(city, query):

    score = 0

    name = normalize(city.name)
    query = normalize(query)

    if name == query:
        score += 100

    elif name.startswith(query):
        score += 50

    elif query in name:
        score += 25

    PRIORITY = [
        "RU","US","JP","GB","DE","FR","IT","ES","CA","AU"
    ]

    if city.country in PRIORITY:
        score += 10


    # ⭐ ADD THIS BLOCK HERE
    MAJOR = {

        "tokyo":"JP",
        "paris":"FR",
        "london":"GB",
        "moscow":"RU",
        "berlin":"DE",
        "rome":"IT"

    }

    if query in MAJOR:

        if city.country == MAJOR[query]:

            score += 40


    return score

async def animate_search(message, lang):

    frames_en = [
        "🔎 Searching.",
        "🔎 Searching..",
        "🔎 Searching..."
    ]

    frames_ru = [
        "🔎 Ищу.",
        "🔎 Ищу..",
        "🔎 Ищу..."
    ]

    frames = frames_ru if lang == "ru" else frames_en

    i = 0

    try:
        while True:
            await message.edit_text(frames[i % 3])
            await asyncio.sleep(0.5)
            i += 1

    except asyncio.CancelledError:
        pass
# -----------------------------
# Handlers
# -----------------------------
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user.id
    set_lang(user, "en")
    await update.message.reply_text(
        "Hello! Please select language to continue / Здравствуйте! Пожалуйста, выберите язык, чтобы продолжить:",
        reply_markup=language_keyboard()
    )


async def handle_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user.id
    lang = get_lang(user)
    set_state(user, "searching")
    animation_task = None

    user_input = update.message.text.strip()

    # Language switch via text
    if user_input.lower() in ["english", "английский"]:
        set_lang(user, "en")
        await update.message.reply_text(
            TEXT["en"]["lang_set"],
            reply_markup=popular_keyboard(
                get_cities(user),
                "en"
            )
        )
        clear_state(user)
        return

    if user_input.lower() in ["russian", "русский"]:
        set_lang(user, "ru")
        await update.message.reply_text(
            TEXT["ru"]["lang_set"],
            reply_markup=popular_keyboard(
                get_cities(user),
                "ru"
            )
        )
        clear_state(user)
        return


    try:
        searching_msg = await update.message.reply_text(
            TEXT[lang]["searching"]
        )
        animation_task = asyncio.create_task(
            animate_search(searching_msg, lang)
        )

        search_query = user_input
        cities = service.search_city(search_query)

        translated = translate_city_to_english(user_input)

        if normalize(translated) != normalize(user_input):
            search_query = translated
            cities = service.search_city(search_query)

        if not cities:
            await searching_msg.edit_text(TEXT[lang]["error"])
            clear_state(user)
            return

        # Remove irrelevant cities
        filtered = []

        query = normalize(search_query)

        for c in cities:

            name = normalize(c.name)

            local_match = False

            if hasattr(c, "local_names") and c.local_names:

                for ln in c.local_names.values():

                    if query in normalize(ln):
                        local_match = True
                        break

            if (
                    name == query or
                    name.startswith(query) or
                    local_match
            ):
                filtered.append(c)

        if filtered:
            cities = filtered
        # Remove duplicates
        unique = {}

        for c in cities:

            key = (c.name, c.country)

            if key not in unique:
                unique[key] = c

        cities = list(unique.values())

        # Sort
        cities = sorted(
            cities,
            key=lambda c: city_score(c, search_query),
            reverse=True
        )

        cities = [c for c in cities if city_score(c, search_query) >= 20]

        cities = cities[:5]

        if not cities:
            await searching_msg.edit_text(TEXT[lang]["error"])
            clear_state(user)
            return

        if len(cities) == 1:
            await show_weather(searching_msg, cities[0], lang)
            clear_state(user)
            return

        set_cities(user, cities)

        await searching_msg.edit_text(
            TEXT[lang]["multiple"],
            reply_markup=cities_keyboard(
                cities,
                lang,
                TEXT[lang]["back"]
            )
        )

    except CityNotFound:
        await searching_msg.edit_text(
            TEXT[lang]["error_city_not_found"]
        )
        clear_state(user)

    except NetworkError:
        await searching_msg.edit_text(
            TEXT[lang]["error_network"]
        )
        clear_state(user)

    except TimeoutError:
        await searching_msg.edit_text(
            TEXT[lang]["error_timeout"]
        )
        clear_state(user)

    except APIError:
        await searching_msg.edit_text(
            TEXT[lang]["error_api"]
        )
        clear_state(user)

    except Exception:
        await searching_msg.edit_text(TEXT[lang]["error"])
        clear_state(user)

    finally:
        if animation_task and not animation_task.done():
            animation_task.cancel()

        clear_state(user)


async def city_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user.id
    lang = get_lang(user)

    # Back button
    if query.data == "back":
        popular_objs = []

        for city in POPULAR_CITIES:

            city_list = service.search_city(city["en"])

            if city_list:
                popular_objs.append(city_list[0])

        set_cities(user, popular_objs)

        await query.message.reply_text(

            TEXT[lang]["start"],

            reply_markup=popular_keyboard(
                popular_objs,
                lang
            )

        )

        return

    # Language selection
    if query.data.startswith("lang_"):

        selected_lang = query.data.split("_")[1]

        set_lang(user, selected_lang)

        popular_objs = []

        for city in POPULAR_CITIES:

            city_list = service.search_city(city["en"])

            if city_list:
                popular_objs.append(city_list[0])

        set_cities(user, popular_objs)

        await query.message.reply_text(

            TEXT[selected_lang]["lang_set"],

            reply_markup=popular_keyboard(
                popular_objs,
                selected_lang
            )

        )

        return

    # Popular city selection
    if query.data.startswith("popular_"):
        index = int(query.data.split("_")[1])
        cities = get_cities(user)
        if not cities or index >= len(cities):
            await query.message.reply_text(TEXT[lang]["error"])
            return
        city = cities[index]
        await show_weather(query, city, lang, callback=True)
        return

    # City selection from multiple search results
    if query.data.startswith("city_"):

        index = int(query.data.split("_")[1])

        cities = get_cities(user)

        if not cities or index >= len(cities):
            await query.message.reply_text(TEXT[lang]["error"])
            return

        city = cities[index]

        await show_weather(query, city, lang, callback=True)

        return

    # City selection from multiple options
    try:
        index = int(query.data.split("_")[1])
    except (IndexError, ValueError):
        await query.message.reply_text(TEXT[lang]["error"])
        return

    cities = get_cities(user)
    if not cities or index >= len(cities):
        await query.message.reply_text(TEXT[lang]["error"])
        return

    city = cities[index]
    await show_weather(query, city, lang, callback=True)


async def show_weather(update_or_query, city, lang, callback=False):
    weather = service.get_weather(city, lang)
    emoji = weather_emoji(getattr(weather, "code", 0))
    flag = country_flag(city.country)

    temp_c = weather.temperature
    temp_f = (temp_c * 9 / 5) + 32
    feels_c = weather.feels_like
    feels_f = (feels_c * 9 / 5) + 32

    # Display names localized
    city_name = city.get_local_name(lang)

    # fallback translation if OpenWeather has no RU name
    if lang == "ru" and city_name == city.name:

        try:

            city_name = GoogleTranslator(
                source='en',
                target='ru'
            ).translate(city.name)

        except Exception:

            city_name = city.name

    country = get_country_name(city.country, lang)

    text = (
        f"{city_name}, {country} {flag}\n\n"
        f"{TEXT[lang]['temp']}: {int(round(temp_c))}°C / {int(round(temp_f))}°F\n"
        f"{TEXT[lang]['feels']}: {int(round(feels_c))}°C / {int(round(feels_f))}°F\n"
        f"{TEXT[lang]['condition']}: {weather.condition} {emoji}"
    )

    if callback:
        await update_or_query.edit_message_text(text)

    elif hasattr(update_or_query, "edit_text"):
        await update_or_query.edit_text(text)

    else:
        await update_or_query.message.reply_text(text)


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user.id
    lang = get_lang(user)
    await update.message.reply_text(TEXT[lang]["help"])

async def weather_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user.id
    lang = get_lang(user)

    popular_objs = []

    for city in POPULAR_CITIES:
        city_list = service.search_city(city["en"])
        if city_list:
            popular_objs.append(city_list[0])

    set_cities(user, popular_objs)

    await update.message.reply_text(
        TEXT[lang]["start"],
        reply_markup=popular_keyboard(popular_objs, lang)
    )