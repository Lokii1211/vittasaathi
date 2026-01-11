import csv
from pathlib import Path

USER_FILE = Path("data/users.csv")

def set_user_language(user_id, language, voice_enabled=False):
    with open(USER_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([user_id, language, voice_enabled])

def get_user_language(user_id):
    if not USER_FILE.exists():
        return "en", False

    with open(USER_FILE, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["user_id"] == user_id:
                return row["language"], row["voice_enabled"]

    return "en", False

