"""
AI-Powered Onboarding Service
Uses OpenAI GPT to understand natural language responses during onboarding
"""

import os
import re
import json
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

class AIOnboardingService:
    """AI-powered onboarding that understands natural language"""
    
    def __init__(self, user_repo):
        self.user_repo = user_repo
        self.api_key = OPENAI_API_KEY
    
    def _call_openai(self, prompt: str, system_message: str = None) -> str:
        """Call OpenAI GPT API"""
        if not self.api_key or len(self.api_key) < 20:
            return None
        
        try:
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": messages,
                    "temperature": 0.3,
                    "max_tokens": 500
                },
                timeout=30
            )
            
            if response.ok:
                return response.json()["choices"][0]["message"]["content"]
            else:
                print(f"OpenAI Error: {response.text}")
                return None
        except Exception as e:
            print(f"OpenAI call failed: {e}")
            return None
    
    def detect_language(self, message: str) -> Optional[str]:
        """Detect which language user wants from their message"""
        msg = message.lower().strip()
        
        # Common greetings should NOT trigger language selection
        greetings = ["hi", "hello", "hey", "hii", "hiii", "namaste", "ok", "yes", "no", "start"]
        if msg in greetings:
            return None  # Show welcome message instead
        
        # Direct language mentions
        language_map = {
            # English variations
            "english": "english", "eng": "english", "en": "english",
            "1": "english",
            
            # Hindi variations
            "hindi": "hindi", "हिंदी": "hindi", "हिन्दी": "hindi",
            "2": "hindi",
            
            # Tamil variations  
            "tamil": "tamil", "தமிழ்": "tamil", "தமிழ": "tamil",
            "3": "tamil",
            
            # Telugu variations
            "telugu": "telugu", "తెలుగు": "telugu",
            "4": "telugu",
            
            # Kannada variations
            "kannada": "kannada", "ಕನ್ನಡ": "kannada",
            "5": "kannada",
            
            # Malayalam variations
            "malayalam": "malayalam", "മലയാളം": "malayalam",
            "6": "malayalam",
            
            # Marathi variations
            "marathi": "marathi", "मराठी": "marathi",
            "7": "marathi",
            
            # Bengali variations
            "bengali": "bengali", "বাংলা": "bengali", "bangla": "bengali",
            "8": "bengali"
        }
        
        # Check direct match
        if msg in language_map:
            return language_map[msg]
        
        # Check if message contains language name
        for key, lang in language_map.items():
            if key in msg and len(key) > 1:  # Avoid matching single digits
                return lang
        
        # Use OpenAI if available for complex cases
        if self.api_key:
            prompt = f"""User said: "{message}"
            
They are choosing their preferred language. Which language did they choose?
Options: english, hindi, tamil, telugu, kannada, malayalam, marathi, bengali

Reply with ONLY the language name in lowercase, or "unknown" if unclear."""
            
            result = self._call_openai(prompt)
            if result and result.strip().lower() in language_map.values():
                return result.strip().lower()
        
        return None
    
    def detect_profession(self, message: str) -> Optional[str]:
        """Detect profession from user message"""
        msg = message.lower().strip()
        
        # Common professions mapping
        profession_map = {
            # Numbers (fallback)
            "1": "Delivery Partner",
            "2": "Cab/Auto Driver", 
            "3": "Daily Wage Worker",
            "4": "Shopkeeper",
            "5": "Student",
            "6": "Homemaker",
            "7": "Salaried Employee",
            "8": "Freelancer",
            "9": "Other",
            
            # Text mappings
            "student": "Student",
            "माणवर": "Student",
            "மாணவர்": "Student",
            "छात्र": "Student",
            
            "teacher": "Salaried Employee",
            "doctor": "Salaried Employee",
            "engineer": "Salaried Employee",
            "it": "Salaried Employee",
            "software": "Salaried Employee",
            "employee": "Salaried Employee",
            "salaried": "Salaried Employee",
            "job": "Salaried Employee",
            "नौकरी": "Salaried Employee",
            
            "housewife": "Homemaker",
            "homemaker": "Homemaker",
            "गृहिणी": "Homemaker",
            "இல்லத்தரசி": "Homemaker",
            
            "driver": "Cab/Auto Driver",
            "ड्राइवर": "Cab/Auto Driver",
            "uber": "Cab/Auto Driver",
            "ola": "Cab/Auto Driver",
            "cab": "Cab/Auto Driver",
            "auto": "Cab/Auto Driver",
            
            "delivery": "Delivery Partner",
            "zomato": "Delivery Partner",
            "swiggy": "Delivery Partner",
            
            "shop": "Shopkeeper",
            "business": "Shopkeeper",
            "दुकान": "Shopkeeper",
            "व्यापार": "Shopkeeper",
            
            "freelance": "Freelancer",
            "freelancer": "Freelancer",
            "self employed": "Freelancer",
            
            "labour": "Daily Wage Worker",
            "worker": "Daily Wage Worker",
            "मजदूर": "Daily Wage Worker",
            "daily wage": "Daily Wage Worker"
        }
        
        # Check direct match
        if msg in profession_map:
            return profession_map[msg]
        
        # Check if any keyword matches
        for key, prof in profession_map.items():
            if key in msg and len(key) > 1:
                return prof
        
        # Use OpenAI for complex cases
        if self.api_key:
            prompt = f"""User said: "{message}" about their profession/job.

Categorize into one of these professions:
- Student
- Salaried Employee (teacher, doctor, engineer, IT, etc.)
- Homemaker (housewife)
- Cab/Auto Driver (uber, ola, taxi)
- Delivery Partner (swiggy, zomato)
- Shopkeeper (business, shop owner)
- Freelancer (self-employed)
- Daily Wage Worker (labour, construction)
- Other

Reply with ONLY the profession category name."""
            
            result = self._call_openai(prompt)
            if result:
                return result.strip()
        
        # Accept any text as profession (2+ chars)
        if len(msg) >= 2:
            return message.strip().title()
        
        return None
    
    def parse_income(self, message: str) -> Optional[int]:
        """Parse income amount from message - handles various formats"""
        msg = message.lower().strip()
        
        # Handle "k" suffix (25k = 25000)
        k_match = re.search(r'(\d+)\s*k\b', msg)
        if k_match:
            return int(k_match.group(1)) * 1000
        
        # Handle "lakh" suffix (2 lakh = 200000)
        lakh_match = re.search(r'(\d+)\s*(?:lakh|lac|lacs)\b', msg)
        if lakh_match:
            return int(lakh_match.group(1)) * 100000
        
        # Remove currency symbols and extract number
        cleaned = re.sub(r'[₹$,\s]', '', msg)
        numbers = re.findall(r'\d+', cleaned)
        
        if numbers:
            amount = int(numbers[0])
            # If very small number, might be in thousands
            if amount < 100 and "hazar" in msg or "thousand" in msg:
                amount = amount * 1000
            return amount if amount > 0 else None
        
        # Use OpenAI for complex cases
        if self.api_key:
            prompt = f"""User said: "{message}" about their monthly income.

Extract the monthly income amount in rupees as an integer.
If they mentioned a range, use the middle value.
If unclear, return 0.

Reply with ONLY the number (no symbols, no text)."""
            
            result = self._call_openai(prompt)
            if result:
                try:
                    return int(re.sub(r'[,\s]', '', result.strip()))
                except:
                    pass
        
        return None
    
    def parse_goals(self, message: str) -> List[str]:
        """Parse financial goals from message"""
        msg = message.lower()
        goals = []
        
        goal_keywords = {
            "1": ["1", "emergency", "fund", "backup", "rainy"],
            "2": ["2", "house", "home", "property", "flat", "apartment", "घर", "வீடு"],
            "3": ["3", "education", "study", "college", "school", "शिक्षा", "கல்வி"],
            "4": ["4", "debt", "loan", "emi", "कर्ज", "கடன்"],
            "5": ["5", "marriage", "wedding", "shaadi", "शादी", "திருமணம்"],
            "6": ["6", "retirement", "retire", "pension", "रिटायरमेंट"],
            "7": ["7", "business", "startup", "shop", "बिजनेस", "தொழில்"],
            "8": ["8", "savings", "save", "general", "बचत", "சேமிப்பு"]
        }
        
        for goal_id, keywords in goal_keywords.items():
            if any(kw in msg for kw in keywords):
                goals.append(goal_id)
        
        # If no matches, try numbers
        if not goals:
            numbers = re.findall(r'[1-8]', msg)
            goals = list(set(numbers))
        
        # Default to general savings if nothing matched
        if not goals:
            goals = ["8"]
        
        return goals[:5]
    
    def get_welcome_message(self, language: str = "english") -> str:
        """Get welcome message for language selection"""
        return """🙏 *Welcome to VittaSaathi!*

I'm your personal financial friend! 💰

Which language do you prefer? Just tell me!

Examples: *English*, *Hindi*, *Tamil*, *Telugu*, *Kannada*

(Or type the language in your preferred script like: हिंदी, தமிழ், తెలుగు)"""
    
    def get_ask_name_message(self, language: str) -> str:
        """Get message asking for name"""
        messages = {
            "english": "📝 Great choice!\n\nWhat's your name?\n\n(Just type your name)",
            "hindi": "📝 बढ़िया!\n\nआपका नाम क्या है?\n\n(बस अपना नाम लिखें)",
            "tamil": "📝 நல்ல தேர்வு!\n\nஉங்கள் பெயர் என்ன?\n\n(உங்கள் பெயரை தட்டச்சு செய்யுங்கள்)",
            "telugu": "📝 మంచి ఎంపిక!\n\nమీ పేరు ఏమిటి?",
            "kannada": "📝 ಒಳ್ಳೆಯ ಆಯ್ಕೆ!\n\nನಿಮ್ಮ ಹೆಸರು ಏನು?"
        }
        return messages.get(language, messages["english"])
    
    def get_ask_profession_message(self, name: str, language: str) -> str:
        """Get message asking for profession"""
        messages = {
            "english": f"""💼 Nice to meet you, {name}!

What do you do for work?

Just tell me! Examples: Student, Teacher, Doctor, IT Employee, Housewife, Driver, Business...""",
            "hindi": f"""💼 आपसे मिलकर खुशी हुई, {name}!

आप क्या काम करते हैं?

बस बताइए! जैसे: छात्र, टीचर, डॉक्टर, IT कर्मचारी, गृहिणी, ड्राइवर, बिजनेस...""",
            "tamil": f"""💼 வணக்கம் {name}!

நீங்கள் என்ன வேலை செய்கிறீர்கள்?

சொல்லுங்கள்! எடுத்துக்காட்டு: மாணவர், ஆசிரியர், மருத்துவர், IT ஊழியர், இல்லத்தரசி, ஓட்டுநர்..."""
        }
        return messages.get(language, messages["english"])
    
    def get_ask_income_message(self, language: str) -> str:
        """Get message asking for income"""
        messages = {
            "english": """💰 Got it!

What's your approximate monthly income?

Just type the amount! Examples: 25000, 50k, 2 lakh...""",
            "hindi": """💰 समझ गया!

आपकी लगभग मासिक आय कितनी है?

बस नंबर लिखें! जैसे: 25000, 50k, 2 लाख...""",
            "tamil": """💰 புரிந்தது!

உங்கள் மாத வருமானம் எவ்வளவு?

தொகையை எழுதுங்கள்! எடுத்துக்காட்டு: 25000, 50k..."""
        }
        return messages.get(language, messages["english"])
    
    def get_ask_goals_message(self, language: str) -> str:
        """Get message asking for financial goals"""
        messages = {
            "english": """🎯 What are your financial goals?

Tell me what you want to achieve! Examples:
• Emergency fund
• Buy a house/home  
• Education
• Pay off loans
• Marriage/Wedding
• Retirement
• Start a business
• General savings

Just type like: 'emergency fund and house' or 'save for education'""",
            "hindi": """🎯 आपके वित्तीय लक्ष्य क्या हैं?

बताइए क्या हासिल करना चाहते हैं! जैसे:
• इमरजेंसी फंड
• घर खरीदना
• शिक्षा
• कर्ज चुकाना
• शादी
• रिटायरमेंट
• बिजनेस

बस लिखें जैसे: 'इमरजेंसी फंड और शादी'""",
            "tamil": """🎯 உங்கள் நிதி இலக்குகள் என்ன?

நீங்கள் என்ன அடைய விரும்புகிறீர்கள்! எடுத்துக்காட்டு:
• அவசர நிதி
• வீடு வாங்க
• கல்வி
• கடன் அடைப்பு
• திருமணம்
• ஓய்வு

இப்படி எழுதுங்கள்: 'அவசர நிதி மற்றும் வீடு'"""
        }
        return messages.get(language, messages["english"])
    
    def get_complete_message(self, user: dict, language: str) -> str:
        """Get onboarding completion message"""
        name = user.get("name", "Friend")
        income = user.get("monthly_income", 0)
        savings = int(income * 0.2)  # 20% savings recommendation
        daily = int((income - savings) / 30)
        
        messages = {
            "english": f"""🎉 *Congratulations, {name}!*

Your VittaSaathi profile is ready!

📊 *Your Financial Plan:*
💰 Monthly Income: ₹{income:,}
💾 Savings Goal: ₹{savings:,}/month (20%)
📅 Daily Budget: ₹{daily:,}

💡 *How to use:*
• "spent 100 on food" → Track expense
• "earned 5000" → Track income
• "balance" → Check status
• "report" → Get summary

Let's start your financial journey! 🚀""",
            "hindi": f"""🎉 *बधाई, {name}!*

आपकी प्रोफाइल तैयार है!

📊 *आपकी प्लान:*
💰 मासिक आय: ₹{income:,}
💾 बचत लक्ष्य: ₹{savings:,}/महीना
📅 दैनिक बजट: ₹{daily:,}

💡 *कैसे इस्तेमाल करें:*
• "100 खाने पर खर्च" → खर्च ट्रैक
• "5000 कमाए" → आय ट्रैक
• "बैलेंस" → स्थिति देखें

शुरू करें! 🚀""",
            "tamil": f"""🎉 *வாழ்த்துக்கள், {name}!*

உங்கள் VittaSaathi சுயவிவரம் தயார்!

📊 *உங்கள் திட்டம்:*
💰 மாத வருமானம்: ₹{income:,}
💾 சேமிப்பு இலக்கு: ₹{savings:,}/மாதம்
📅 தினசரி பட்ஜெட்: ₹{daily:,}

தொடங்குவோம்! 🚀"""
        }
        return messages.get(language, messages["english"])
    
    def process_onboarding(self, phone: str, message: str, user: dict) -> dict:
        """Process onboarding message using AI understanding"""
        step = user.get("onboarding_step", "language")
        language = user.get("preferred_language", "english")
        
        # Check for restart/language change commands
        msg_lower = message.lower().strip()
        change_lang_triggers = ["restart", "start over", "reset", "change language", 
                                "change lang", "different language", "भाषा बदलें", 
                                "மொழி மாற்று", "భాష మార్చు"]
        
        if msg_lower in change_lang_triggers or "change" in msg_lower and "language" in msg_lower:
            self.user_repo.update_user(phone, {"onboarding_step": "language"})
            return {"text": self.get_welcome_message(), "step": "language"}
        
        # Step 1: Language Selection
        if step == "language" or step == "language_selection":
            detected_lang = self.detect_language(message)
            
            if detected_lang:
                lang_names = {
                    "english": "English", "hindi": "हिंदी", "tamil": "தமிழ்",
                    "telugu": "తెలుగు", "kannada": "ಕನ್ನಡ", "malayalam": "മലയാളം"
                }
                
                self.user_repo.update_user(phone, {
                    "preferred_language": detected_lang,
                    "language": detected_lang,
                    "onboarding_step": "name"
                })
                
                confirm = f"✅ Language set to *{lang_names.get(detected_lang, detected_lang)}*! 🎉\n\n"
                return {
                    "text": confirm + self.get_ask_name_message(detected_lang),
                    "step": "name"
                }
            else:
                return {
                    "text": self.get_welcome_message(),
                    "step": "language"
                }
        
        # Step 2: Name
        elif step == "name":
            name = message.strip()
            if len(name) >= 2 and len(name) <= 50:
                self.user_repo.update_user(phone, {
                    "name": name,
                    "onboarding_step": "profession"
                })
                return {
                    "text": self.get_ask_profession_message(name, language),
                    "step": "profession"
                }
            else:
                return {
                    "text": self.get_ask_name_message(language),
                    "step": "name"
                }
        
        # Step 3: Profession
        elif step == "profession":
            profession = self.detect_profession(message)
            
            if profession:
                self.user_repo.update_user(phone, {
                    "profession": profession,
                    "onboarding_step": "income"
                })
                return {
                    "text": self.get_ask_income_message(language),
                    "step": "income"
                }
            else:
                name = user.get("name", "Friend")
                return {
                    "text": self.get_ask_profession_message(name, language),
                    "step": "profession"
                }
        
        # Step 4: Income
        elif step == "income":
            income = self.parse_income(message)
            
            if income and income >= 100:
                self.user_repo.update_user(phone, {
                    "monthly_income": income,
                    "onboarding_step": "goals"
                })
                return {
                    "text": self.get_ask_goals_message(language),
                    "step": "goals"
                }
            else:
                return {
                    "text": self.get_ask_income_message(language),
                    "step": "income"
                }
        
        # Step 5: Goals
        elif step == "goals":
            goals = self.parse_goals(message)
            user_data = self.user_repo.get_user(phone)
            income = user_data.get("monthly_income", 30000)
            savings = int(income * 0.2)
            daily = int((income - savings) / 30)
            
            self.user_repo.update_user(phone, {
                "financial_goals": goals,
                "savings_target": savings,
                "daily_budget": daily,
                "onboarding_step": "complete",
                "onboarding_complete": True
            })
            
            updated_user = self.user_repo.get_user(phone)
            return {
                "text": self.get_complete_message(updated_user, language),
                "step": "complete",
                "complete": True
            }
        
        # Default: Start over
        return {
            "text": self.get_welcome_message(),
            "step": "language"
        }


# Singleton instance
_ai_onboarding = None

def get_ai_onboarding(user_repo):
    """Get AI onboarding service instance"""
    global _ai_onboarding
    if _ai_onboarding is None:
        _ai_onboarding = AIOnboardingService(user_repo)
    return _ai_onboarding
