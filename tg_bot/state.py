users_lang = {}
users_cities = {}

def get_lang(user_id):
    return users_lang.get(user_id, "en")

def set_lang(user_id, lang):
    users_lang[user_id] = lang

def set_cities(user_id, cities):
    users_cities[user_id] = cities

def get_cities(user_id):
    return users_cities.get(user_id, [])