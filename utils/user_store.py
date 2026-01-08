# Simple in-memory user store (safe version)

USERS_DB = {}


def get_user(phone: str):
    return USERS_DB.get(phone)


def create_user(phone: str):
    USERS_DB[phone] = {
        "phone": phone,
        "name": None,
        "language": None,
        "onboarding_step": "NAME"
    }
    return USERS_DB[phone]


def ensure_user(phone: str):
    if phone not in USERS_DB:
        return create_user(phone)
    return USERS_DB[phone]


def save_name(phone: str, name: str):
    user = ensure_user(phone)
    user["name"] = name
    user["onboarding_step"] = "LANGUAGE"


def save_language(phone: str, language: str):
    user = ensure_user(phone)
    user["language"] = language
    user["onboarding_step"] = "DONE"
