"""
AI Personality Service
======================
Gives VittaSaathi a friendly, relatable personality
"""
import random
from datetime import datetime
from typing import Dict, List


class PersonalityService:
    """AI personality and conversational features"""
    
    def __init__(self):
        self.greetings = self._load_greetings()
        self.encouragements = self._load_encouragements()
        self.jokes = self._load_jokes()
        self.emojis = self._load_emojis()
    
    def _load_greetings(self) -> Dict[str, Dict[str, List[str]]]:
        """Time-based greetings in multiple languages"""
        return {
            "morning": {
                "en": [
                    "Good morning, {name}! ☀️ Ready to crush your financial goals?",
                    "Rise and shine, {name}! 🌅 A new day to earn and save!",
                    "Morning, {name}! ☕ Let's make today profitable!",
                ],
                "hi": [
                    "सुप्रभात, {name}! ☀️ आज कमाने का दिन है!",
                    "गुड मॉर्निंग, {name}! 🌅 चलो आज पैसे बचाते हैं!",
                    "उठो {name}! ☕ नया दिन, नई कमाई!",
                ],
                "ta": [
                    "காலை வணக்கம், {name}! ☀️",
                    "சுப்ரபாத், {name}! 🌅",
                ],
                "te": [
                    "శుభోదయం, {name}! ☀️",
                    "గుడ్ మార్నింగ్, {name}! 🌅",
                ]
            },
            "afternoon": {
                "en": [
                    "Hey {name}! 🌤️ How's the afternoon treating you?",
                    "Good afternoon, {name}! 💪 Keep that hustle going!",
                ],
                "hi": [
                    "हाय {name}! 🌤️ दोपहर कैसी रही?",
                    "नमस्ते {name}! 💪 कमाई जारी रखो!",
                ],
            },
            "evening": {
                "en": [
                    "Good evening, {name}! 🌆 Time to count today's earnings!",
                    "Hey {name}! 🌙 How was your day? Let's track expenses!",
                ],
                "hi": [
                    "शुभ संध्या, {name}! 🌆 आज की कमाई गिनें!",
                    "हाय {name}! 🌙 दिन कैसा रहा? खर्च नोट करें!",
                ],
            },
            "night": {
                "en": [
                    "Still up, {name}? 🌃 Don't forget to rest!",
                    "Night owl, {name}? 🦉 Quick update and then sleep!",
                ],
                "hi": [
                    "अभी जागे हो, {name}? 🌃 आराम करो!",
                    "रात को काम, {name}? 🦉 जल्दी सो जाओ!",
                ],
            }
        }
    
    def _load_encouragements(self) -> Dict[str, List[str]]:
        return {
            "en": [
                "You're doing amazing! 💪",
                "Every rupee saved is a rupee earned! 💰",
                "Small steps lead to big savings! 🚀",
                "Consistency is key! Keep it up! 🔑",
                "Your future self will thank you! 🙏",
                "Financial freedom is closer than you think! ✨",
                "Proud of you for tracking! 📊",
                "You're one step ahead now! 👏",
            ],
            "hi": [
                "बहुत अच्छे! 💪",
                "हर बचाया रुपया कमाया रुपया है! 💰",
                "छोटे कदम बड़ी बचत! 🚀",
                "निरंतरता सफलता की कुंजी है! 🔑",
                "भविष्य का तुम धन्यवाद देगा! 🙏",
                "आर्थिक आज़ादी पास है! ✨",
                "ट्रैक करने पर गर्व है! 📊",
                "एक कदम आगे निकल गए! 👏",
            ],
        }
    
    def _load_jokes(self) -> Dict[str, List[str]]:
        """Finance-related jokes"""
        return {
            "en": [
                "Why did the banker switch careers? He lost interest! 😄",
                "Money talks... mine just says 'goodbye'! 👋",
                "I'm not saying I'm broke, but my piggy bank asked for a loan! 🐷",
                "Saving money is like a marathon. I'm still at the starting line! 🏃",
            ],
            "hi": [
                "पैसा बोलता है... मेरा कहता है 'बाय बाय'! 😄",
                "बचत मैराथन है, मैं अभी शुरू में हूं! 🏃",
                "मेरे गुल्लक ने मुझसे उधार माँगा! 🐷",
            ],
        }
    
    def _load_emojis(self) -> Dict[str, str]:
        return {
            "income": "💰💵🤑",
            "expense": "💸🛒🧾",
            "savings": "🏦💾💎",
            "goal": "🎯🏆🌟",
            "warning": "⚠️🚨⚡",
            "success": "✅🎉👏",
            "health": "🏥💚❤️",
            "fraud": "🛡️🔒🚫",
        }
    
    def get_greeting(self, name: str, language: str = "en") -> str:
        """Get time-appropriate greeting"""
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            period = "morning"
        elif 12 <= hour < 17:
            period = "afternoon"
        elif 17 <= hour < 21:
            period = "evening"
        else:
            period = "night"
        
        greetings = self.greetings.get(period, {}).get(language, self.greetings[period]["en"])
        greeting = random.choice(greetings).format(name=name)
        
        return greeting
    
    def get_encouragement(self, language: str = "en") -> str:
        """Get random encouragement"""
        encouragements = self.encouragements.get(language, self.encouragements["en"])
        return random.choice(encouragements)
    
    def get_joke(self, language: str = "en") -> str:
        """Get random finance joke"""
        jokes = self.jokes.get(language, self.jokes["en"])
        return random.choice(jokes)
    
    def add_personality(self, message: str, context: str = "neutral", language: str = "en") -> str:
        """Add personality elements to message"""
        
        # 20% chance to add encouragement
        if random.random() < 0.2 and context in ["income", "savings"]:
            message += f"\n\n{self.get_encouragement(language)}"
        
        # 5% chance to add joke (not on warnings)
        if random.random() < 0.05 and context not in ["warning", "fraud"]:
            message += f"\n\n😄 *Fun fact:* {self.get_joke(language)}"
        
        return message
    
    def get_streak_celebration(self, streak: int, language: str = "en") -> str:
        """Celebrate user streaks"""
        if streak == 7:
            return "🔥 1 WEEK STREAK! You're on fire!" if language == "en" else "🔥 1 हफ्ते का स्ट्रीक! शानदार!"
        elif streak == 30:
            return "🏆 1 MONTH STREAK! Incredible discipline!" if language == "en" else "🏆 1 महीने का स्ट्रीक! गजब!"
        elif streak == 100:
            return "👑 100 DAYS! You're a financial champion!" if language == "en" else "👑 100 दिन! आप चैंपियन हो!"
        elif streak % 10 == 0 and streak > 0:
            return f"✨ {streak} day streak! Amazing!" if language == "en" else f"✨ {streak} दिन का स्ट्रीक!"
        return ""


personality_service = PersonalityService()
