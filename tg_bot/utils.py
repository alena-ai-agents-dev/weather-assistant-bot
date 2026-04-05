import pycountry
from babel import Locale


def get_country_name(code, lang):

    try:

        country = pycountry.countries.get(alpha_2=code)

        if not country:
            return code

        locale = Locale.parse(lang)

        return locale.territories.get(
            country.alpha_2,
            country.name
        )

    except Exception:
        return code


def weather_emoji(code):
    """Return emoji based on OpenWeather condition code"""
    if code == 800:
        return "☀️"  # clear
    elif 801 <= code <= 804:
        return "☁️"  # clouds
    elif 500 <= code <= 531:
        return "🌧️"  # rain
    elif 300 <= code <= 321:
        return "🌦️"  # drizzle
    elif 600 <= code <= 622:
        return "❄️"  # snow
    elif 200 <= code <= 232:
        return "⛈️"  # thunderstorm
    elif 701 <= code <= 781:
        return "🌫️"  # fog/mist/haze
    else:
        return "🌍"  # unknown / default

def country_flag(code):

    return "".join(
        chr(127397 + ord(c))
        for c in code.upper()
    )