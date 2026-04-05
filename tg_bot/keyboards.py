from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from tg_bot.utils import get_country_name
from deep_translator import GoogleTranslator
from core.constants import POPULAR_CITIES


def popular_keyboard(cities, lang):

    buttons = []

    for i, c in enumerate(cities):

        name = c.get_local_name(lang)

        buttons.append([

            InlineKeyboardButton(
                name,
                callback_data=f"popular_{i}"
            )

        ])

    return InlineKeyboardMarkup(buttons)


def language_keyboard():

    buttons = [

        [InlineKeyboardButton(
            "English",
            callback_data="lang_en"
        )],

        [InlineKeyboardButton(
            "Русский",
            callback_data="lang_ru"
        )]

    ]

    return InlineKeyboardMarkup(buttons)


def cities_keyboard(cities, lang, back):

    buttons = []

    for i, city in enumerate(cities):

        city_name = city.get_local_name(lang)

        if lang == "ru" and city_name == city.name:

            try:

                city_name = GoogleTranslator(
                    source='en',
                    target='ru'
                ).translate(city.name)

            except Exception:

                city_name = city.name

        country_name = get_country_name(
            city.country,
            lang
        )

        buttons.append([

            InlineKeyboardButton(

                f"{city_name}, {country_name}",

                callback_data=f"city_{i}"

            )

        ])

    buttons.append([

        InlineKeyboardButton(
            back,
            callback_data="back"
        )

    ])

    return InlineKeyboardMarkup(buttons)