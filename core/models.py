class City:
    def __init__(self, name, country, state, lat, lon, local_names=None):
        self.name = name
        self.country = country
        self.state = state
        self.lat = lat
        self.lon = lon
        self.local_names = local_names or {}

    def get_local_name(self, lang="en"):
        return self.local_names.get(lang, self.name)


class Weather:
    def __init__(self, temp_c, feels_like, condition, code=None):
        self.temperature = temp_c
        self.feels_like = feels_like
        self.condition = condition
        self.code = code