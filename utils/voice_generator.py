from gtts import gTTS
from pathlib import Path

VOICE_DIR = Path("data/voices")
VOICE_DIR.mkdir(exist_ok=True)

def generate_voice(text, language="en"):
    file_path = VOICE_DIR / "alert.mp3"
    tts = gTTS(text=text, lang=language)
    tts.save(file_path)
    return str(file_path)
