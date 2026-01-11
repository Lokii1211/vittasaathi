"""
Message Builder Service - Build localized messages for WhatsApp
"""
from datetime import datetime
from typing import Dict, List
from pathlib import Path


class MessageBuilder:
    """Build localized messages for WhatsApp"""
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict:
        return {
            "welcome": {
                "en": "🙏 Welcome to MoneyViya - Your Financial Advisor!\n\nWhat's your name?",
                "hi": "🙏 MoneyViya में स्वागत है!\n\nआपका नाम क्या है?",
                "ta": "🙏 MoneyViya க்கு வரவேற்கிறோம்!\n\nஉங்கள் பெயர் என்ன?",
                "te": "🙏 MoneyViya కి స్వాగతం!\n\nమీ పేరు ఏమిటి?",
            },
            "ask_language": {
                "en": "Hi {name}! 👋\n\nChoose language:\n1️⃣ English\n2️⃣ हिंदी\n3️⃣ தமிழ்\n4️⃣ తెలుగు",
            },
            "ask_profession": {
                "en": "What's your profession? 💼\n(e.g., Swiggy driver, freelancer)",
                "hi": "आप क्या करते हैं? 💼",
                "ta": "நீங்கள் என்ன வேலை? 💼",
                "te": "మీరు ఏం పని? 💼",
            },
            "ask_income": {
                "en": "Monthly income? 💵 (e.g., 25000)",
                "hi": "मासिक आय? 💵",
                "ta": "மாத வருமானம்? 💵",
                "te": "నెల ఆదాయం? 💵",
            },
            "ask_dependents": {
                "en": "How many dependents? 👨‍👩‍👧‍👦",
                "hi": "कितने आश्रित? 👨‍👩‍👧‍👦",
                "ta": "எத்தனை பேர்? 👨‍👩‍👧‍👦",
                "te": "ఎంతమంది? 👨‍👩‍👧‍👦",
            },
            "ask_savings": {
                "en": "Current savings? 🏦 (0 if none)",
                "hi": "बचत कितनी? 🏦",
                "ta": "சேமிப்பு? 🏦",
                "te": "పొదుపు? 🏦",
            },
            "ask_debt": {
                "en": "Any loans/debts? 💳 (0 if none)",
                "hi": "कर्ज है? 💳",
                "ta": "கடன் உள்ளதா? 💳",
                "te": "అప్పు ఉందా? 💳",
            },
            "ask_goals": {
                "en": "Financial goals?\n1️⃣ Emergency Fund\n2️⃣ Pay Debt\n3️⃣ Child Education\n4️⃣ Buy Home\n5️⃣ Vehicle\n6️⃣ Wedding\n7️⃣ Retirement",
                "hi": "लक्ष्य?\n1️⃣ इमरजेंसी\n2️⃣ कर्ज चुकाना\n3️⃣ पढ़ाई\n4️⃣ घर\n5️⃣ गाड़ी\n6️⃣ शादी\n7️⃣ रिटायरमेंट",
            },
            "onboarding_complete": {
                "en": "🎉 Profile ready, {name}!\n\n💰 Say \"earned 500\" or \"spent 100\"\n📊 Say \"summary\" for reports\n💡 Say \"advice\" for tips\n🎯 Say \"goals\" for progress",
                "hi": "🎉 प्रोफाइल तैयार, {name}!\n\n💰 \"500 कमाए\" या \"100 खर्च\" बोलें\n📊 \"सारांश\" बोलें\n💡 \"सलाह\" बोलें",
            },
            "income_recorded": {
                "en": "✅ ₹{amount} income recorded! 💰",
                "hi": "✅ ₹{amount} आमदनी दर्ज! 💰",
                "ta": "✅ ₹{amount} வருமானம்! 💰",
                "te": "✅ ₹{amount} ఆదాయం! 💰",
            },
            "expense_recorded": {
                "en": "✅ ₹{amount} expense recorded!\n📊 Today left: ₹{remaining}",
                "hi": "✅ ₹{amount} खर्च दर्ज!\n📊 आज बाकी: ₹{remaining}",
            },
            "daily_summary": {
                "en": "📊 Today\n💰 Income: ₹{income}\n💸 Expense: ₹{expense}\n📈 Net: ₹{net}",
                "hi": "📊 आज\n💰 आय: ₹{income}\n💸 खर्च: ₹{expense}\n📈 नेट: ₹{net}",
            },
            "fraud_blocked": {
                "en": "🚨 FRAUD ALERT!\n₹{amount} blocked\nReply YES if you, NO if not",
                "hi": "🚨 फ्रॉड अलर्ट!\n₹{amount} ब्लॉक\nYES/NO भेजें",
            },
            "help_menu": {
                "en": "📚 Help\n💰 Track: \"earned 500\" \"spent 100\"\n📊 Reports: \"summary\" \"monthly\"\n💡 Advice: \"advice\" \"loan\" \"invest\"\n🎯 Goals: \"my goals\"",
                "hi": "📚 मदद\n💰 ट्रैक: \"500 कमाए\" \"100 खर्च\"\n📊 रिपोर्ट: \"सारांश\"\n💡 सलाह: \"सलाह\" \"लोन\" \"निवेश\"",
            },
            "error_generic": {
                "en": "❌ Didn't understand. Say \"help\"",
                "hi": "❌ समझा नहीं। \"help\" बोलें",
            },
        }
    
    def get_message(self, key: str, lang: str = "en", **kwargs) -> str:
        template = self.templates.get(key, {})
        msg = template.get(lang) or template.get("en", "")
        if kwargs:
            try:
                msg = msg.format(**kwargs)
            except:
                pass
        return msg
    
    def build_income_response(self, amount: int, category: str, lang: str = "en") -> str:
        return self.get_message("income_recorded", lang, amount=f"{amount:,}")
    
    def build_expense_response(self, amount: int, category: str, remaining: int, lang: str = "en") -> str:
        return self.get_message("expense_recorded", lang, amount=f"{amount:,}", remaining=f"{remaining:,}")
    
    def build_daily_summary(self, income: int, expense: int, target: int, lang: str = "en") -> str:
        return self.get_message("daily_summary", lang, income=f"{income:,}", expense=f"{expense:,}", net=f"{income-expense:,}")
    
    def build_fraud_alert(self, amount: int, risk: float, reasons: List[str], lang: str = "en") -> str:
        return self.get_message("fraud_blocked", lang, amount=f"{amount:,}")
    
    def build_onboarding_message(self, step: str, lang: str = "en", **kwargs) -> str:
        step_map = {"NAME": "welcome", "LANGUAGE": "ask_language", "PROFESSION": "ask_profession",
                   "MONTHLY_INCOME": "ask_income", "DEPENDENTS": "ask_dependents", 
                   "CURRENT_SAVINGS": "ask_savings", "CURRENT_DEBT": "ask_debt",
                   "GOALS": "ask_goals", "DONE": "onboarding_complete"}
        return self.get_message(step_map.get(step, "welcome"), lang, **kwargs)


message_builder = MessageBuilder()

