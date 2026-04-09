import requests
import os
from dotenv import load_dotenv
from core.models import City, Weather
from core.errors import CityNotFound, NetworkError, TimeoutError
from core.geonames_db import GeoNamesDB
from core.config import Config

load_dotenv()


class WeatherService:
    def __init__(self):
        self.api_key = Config.OPENWEATHER_API_KEY
        self.geo_url = "http://api.openweathermap.org/geo/1.0/direct"
        self.weather_url = "https://api.openweathermap.org/data/2.5/weather"
        self.geodb = GeoNamesDB()


    def search_city(self, city_name):
        """Search city by raw input; returns list of City objects"""
        try:
            params = {
                "q": city_name,
                "limit": 10,
                "appid": self.api_key
            }
            r = requests.get(self.geo_url, params=params, timeout=Config.REQUEST_TIMEOUT)

            r.raise_for_status()
            data = r.json()

            if not data:
                raise CityNotFound()

            unique = {}

            for c in data:


                key = (c["name"].lower(), c["country"], c.get("state", ""))

                if key not in unique:
                    # Validate using GeoNames
                    if not self.geodb.is_real_city(
                            c["name"],
                            c["country"]
                    ):
                        continue

                    unique[key] = City(

                        name=c["name"],

                        country=c["country"],

                        state=c.get("state", ""),

                        lat=round(c["lat"], 4),

                        lon=round(c["lon"], 4),

                        local_names=c.get("local_names", {})

                    )


            return list(unique.values())[:5]

        except requests.exceptions.ConnectionError:
            raise NetworkError()
        except requests.exceptions.Timeout:
            raise TimeoutError()
        except requests.exceptions.HTTPError:
            raise APIError()

    def get_weather(self, city, lang="en"):
        try:
            params = {
                "lat": city.lat,
                "lon": city.lon,
                "appid": self.api_key,
                "units": "metric",
                "lang": "ru" if lang == "ru" else "en"
            }
            r = requests.get(self.weather_url, params=params, timeout=Config.REQUEST_TIMEOUT)
            r.raise_for_status()
            data = r.json()
            return Weather(
                temp_c=data["main"]["temp"],
                feels_like=data["main"]["feels_like"],
                condition=data["weather"][0]["description"],
                code=data["weather"][0]["id"]
            )
        except requests.exceptions.ConnectionError:
            raise NetworkError()
        except requests.exceptions.Timeout:
            raise TimeoutError()