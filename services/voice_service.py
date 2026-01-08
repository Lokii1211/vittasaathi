"""
Voice Service - Text-to-Speech and Voice Message Handling
"""
from pathlib import Path
from datetime import datetime
import sys

sys.path.append(str(Path(__file__).parent.parent))
from config import VOICES_DIR

try:
    from gtts import gTTS
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False


class VoiceService:
    """Generate and handle voice messages"""
    
    def __init__(self):
        VOICES_DIR.mkdir(exist_ok=True)
    
    def generate_voice(self, text: str, language: str = "en", filename: str = None) -> str:
        """Generate voice message from text"""
        if not TTS_AVAILABLE:
            return None
        
        lang_map = {"en": "en", "hi": "hi", "ta": "ta", "te": "te", "kn": "kn", "ml": "ml"}
        tts_lang = lang_map.get(language, "en")
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"voice_{timestamp}.mp3"
        
        file_path = VOICES_DIR / filename
        
        try:
            tts = gTTS(text=text, lang=tts_lang)
            tts.save(str(file_path))
            return str(file_path)
        except Exception as e:
            print(f"TTS Error: {e}")
            return None
    
    def generate_greeting(self, name: str, language: str = "en") -> str:
        """Generate morning greeting voice"""
        greetings = {
            "en": f"Good morning {name}! Time to track your income and expenses.",
            "hi": f"सुप्रभात {name}! आज की कमाई और खर्च बताइए।",
            "ta": f"காலை வணக்கம் {name}! இன்றைய வருமானம் மற்றும் செலவுகளை பதிவு செய்யுங்கள்.",
            "te": f"శుభోదయం {name}! ఈరోజు ఆదాయం మరియు ఖర్చులు నమోదు చేయండి.",
        }
        text = greetings.get(language, greetings["en"])
        return self.generate_voice(text, language, f"greeting_{name.lower()}.mp3")
    
    def generate_fraud_alert_voice(self, amount: int, language: str = "en") -> str:
        """Generate fraud alert voice message"""
        alerts = {
            "en": f"Warning! A suspicious transaction of {amount} rupees was detected. Please check your WhatsApp immediately and reply YES or NO.",
            "hi": f"चेतावनी! {amount} रुपये का संदिग्ध लेनदेन पाया गया। कृपया तुरंत WhatsApp देखें और YES या NO भेजें।",
            "ta": f"எச்சரிக்கை! {amount} ரூபாய் சந்தேகமான பரிவர்த்தனை கண்டறியப்பட்டது. உடனே WhatsApp பாருங்கள்.",
            "te": f"హెచ్చరిక! {amount} రూపాయల అనుమానాస్పద లావాదేవీ కనుగొనబడింది. దయచేసి WhatsApp తనిఖీ చేయండి.",
        }
        text = alerts.get(language, alerts["en"])
        return self.generate_voice(text, language, f"fraud_alert_{amount}.mp3")
    
    def generate_summary_voice(self, income: int, expense: int, language: str = "en") -> str:
        """Generate daily summary voice"""
        net = income - expense
        summaries = {
            "en": f"Today you earned {income} rupees and spent {expense} rupees. Your net savings is {net} rupees.",
            "hi": f"आज आपने {income} रुपये कमाए और {expense} रुपये खर्च किए। आपकी नेट बचत {net} रुपये है।",
            "ta": f"இன்று நீங்கள் {income} ரூபாய் சம்பாதித்தீர்கள், {expense} ரூபாய் செலவழித்தீர்கள். உங்கள் சேமிப்பு {net} ரூபாய்.",
            "te": f"ఈరోజు మీరు {income} రూపాయలు సంపాదించారు, {expense} రూపాయలు ఖర్చు చేశారు. మీ పొదుపు {net} రూపాయలు.",
        }
        text = summaries.get(language, summaries["en"])
        return self.generate_voice(text, language)


voice_service = VoiceService()
