users_lang = {}
users_cities = {}
users_session = {}

def get_lang(user_id):
    return users_lang.get(user_id, "en")

def set_lang(user_id, lang):
    users_lang[user_id] = lang

def set_cities(user_id, cities):
    users_cities[user_id] = cities

def get_cities(user_id):
    return users_cities.get(user_id, [])

# ✅ NEW SESSION STATE
def set_state(user_id, state):
    users_session[user_id] = state

def get_state(user_id):
    return users_session.get(user_id, "idle")

def clear_state(user_id):
    users_session[user_id] = "idle"