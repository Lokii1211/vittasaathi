"""
Smart Onboarding Service with Multi-Language Support
Handles complete user onboarding with goals, income, and personalized plans
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import re

# Language translations for onboarding
ONBOARDING_MESSAGES = {
    "english": {
        "welcome": """🙏 *Welcome to VittaSaathi!*

I'm your personal financial friend! 💰

Which language do you prefer?

Just type: *English*, *Hindi*, or *Tamil*

(Or type: తెలుగు, ಕನ್ನಡ, മലയാളം, मराठी, বাংলা)""",
        
        "lang_set": "✅ Language set to *English*! 🎉",
        
        "ask_name": """📝 Great!

What's your name?

(Just type your name)""",
        
        "ask_profession": """💼 Nice to meet you, {name}!

What do you do for work?

Just tell me! Examples: Student, Teacher, Doctor, IT Employee, Housewife, Driver, Business, Freelancer...""",
        
        "ask_income": """💰 Got it!

What's your approximate monthly income?

Just type the amount! Examples: 25000, 50000, 15k...""",
        
        "ask_goals": """🎯 Great! What are your financial goals?

Tell me what you want to achieve! Examples:
• Emergency fund
• Save for house/home
• Education
• Pay off loans
• Marriage
• Retirement
• Start business
• General savings

Just type like: 'emergency fund and house' or 'education, marriage'""",
        
        "ask_savings_target": """📊 Almost done!

How much do you want to save each month?

Your income: ₹{income}
Suggested (20%): ₹{suggested}

Just type an amount like: 5000, 10000, 10k...""",
        
        "complete": """🎉 *Congratulations, {name}!*

Your VittaSaathi profile is ready!

📊 *Your Financial Plan:*
💰 Monthly Income: ₹{income}
💾 Savings Goal: ₹{savings}/month
📅 Daily Budget: ₹{daily_budget}

💡 *How to use:*
• "spent 100 on food" → Track expense
• "earned 5000" → Track income  
• "balance" → See your status
• "help" → All commands

Let's start! 🚀""",
        
        "returning_user": """👋 *Welcome back, {name}!*

Good to see you again! 😊

What would you like to do?
• Track expense: "spent 100 on food"
• Track income: "earned 5000"
• Check balance: "balance"
• Get report: "report"
• Need help: 'help'""",
        
        "lang_set": "✅ Language set to *English*! 🎉",
        
        "ask_name": """📝 Great choice!

What's your name?

(Just type your name)""",
        
        "ask_profession": """💼 Nice to meet you, {name}! 

What do you do for work?

Just type it! Examples: Student, Housewife, IT Employee, Delivery Partner, Small Business, Teacher, Doctor, etc.""",
        
        "ask_income": """💰 Got it!

What's your approximate *monthly income*?

Just type the number! Example: 50000""",
        
        "ask_goals": """🎯 Now let's set your financial goals!

What do you want to achieve?

1️⃣ 🏦 Build Emergency Fund (3-6 months expenses)
2️⃣ 🏠 Save for House/Down Payment
3️⃣ 📚 Save for Education
4️⃣ 💳 Pay off Debt/Loans
5️⃣ 💒 Save for Marriage
6️⃣ 👴 Retirement Savings
7️⃣ 🏪 Start a Business
8️⃣ 💰 General Savings

You can select multiple! Reply like "1,3,5" or just "1".""",
        
        "ask_savings_target": """📊 Almost done!

How much do you want to *save each month*?

Based on your income of ₹{income}, we suggest saving at least ₹{suggested} (20%)

(Type your target, e.g., "5000")""",
        
        "complete": """🎉 *Congratulations, {name}!*

Your VittaSaathi profile is ready!

📊 *Your Personalized Financial Plan:*

💰 Monthly Income: ₹{income}
💾 Savings Goal: ₹{savings}/month ({percent}%)
📅 Daily Spending Budget: ₹{daily_budget}
🎯 Focus: {primary_goal}

*Your Goals:*
{goals_list}

💡 *Quick Tips to Start:*
• Say "spent 100 on food" to track expenses
• Say "earned 500" to track income
• Say "balance" to see your status
• Say "report" for a summary

Let's start your financial journey! 🚀""",
        
        "invalid_choice": "❌ I didn't understand. Please reply with a valid number.",
        "invalid_amount": "❌ Please enter a valid amount (numbers only, e.g., 15000)"
    },
    
    "hindi": {
        "welcome": """🙏 *VittaSaathi में स्वागत है!*

मैं आपका वित्तीय मित्र हूं! 💰

आप कौन सी भाषा पसंद करते हैं?

बस लिखें: *Hindi*, *English*, या *Tamil*""",
        
        "lang_set": "✅ भाषा *हिंदी* में सेट! 🎉",
        
        "ask_name": """📝 बढ़िया!

आपका नाम क्या है?

(बस अपना नाम लिखें)""",
        
        "ask_profession": """💼 आपसे मिलकर खुशी हुई, {name}!

आप क्या काम करते हैं?

बस बताइए! जैसे: छात्र, टीचर, डॉक्टर, IT कर्मचारी, गृहिणी, ड्राइवर, बिजनेस...""",
        
        "ask_income": """💰 समझ गया!

आपकी लगभग मासिक आय कितनी है?

बस नंबर लिखें! जैसे: 25000, 50000, 15k...""",
        
        "ask_goals": """🎯 आपके वित्तीय लक्ष्य क्या हैं?

बताइए क्या हासिल करना चाहते हैं! जैसे:
• इमरजेंसी फंड
• घर के लिए बचत
• शिक्षा
• कर्ज चुकाना
• शादी
• रिटायरमेंट
• बिजनेस शुरू करना

बस लिखें जैसे: "इमरजेंसी फंड और शादी" """,
        
        "ask_savings_target": """📊 लगभग हो गया!

हर महीने कितना बचाना चाहते हैं?

आपकी आय: ₹{income}
सुझाव (20%): ₹{suggested}

बस राशि लिखें जैसे: 5000, 10000...""",
        
        "complete": """🎉 *बधाई, {name}!*

आपकी प्रोफाइल तैयार है!

📊 *आपकी प्लान:*
💰 मासिक आय: ₹{income}
💾 बचत लक्ष्य: ₹{savings}/महीना
📅 दैनिक बजट: ₹{daily_budget}

💡 *कैसे इस्तेमाल करें:*
• "100 खाने पर खर्च" → खर्च ट्रैक
• "5000 कमाए" → आय ट्रैक
• "बैलेंस" → स्थिति देखें
• "help" → सभी कमांड

शुरू करें! 🚀""",
        
        "returning_user": """👋 *फिर से स्वागत, {name}!*

आपको देखकर अच्छा लगा! 😊

क्या करना चाहते हैं?
• "100 खाने पर खर्च" → खर्च ट्रैक
• "5000 कमाए" → आय ट्रैक
• "बैलेंस" → स्थिति देखें""",
        
        "invalid_choice": "❌ समझ नहीं आया। कृपया दोबारा बताएं।",
        "invalid_amount": "❌ कृपया सही राशि लिखें (जैसे 15000)"
    },
    
    "tamil": {
        "welcome": """🙏 *VittaSaathi வரவேற்கிறோம்!*

நான் உங்கள் நிதி நண்பன்!

மொழி தேர்ந்தெடுக்கவும்:

1️⃣ English
2️⃣ हिंदी
3️⃣ தமிழ்
4️⃣ తెలుగు
5️⃣ ಕನ್ನಡ

எண் அனுப்புங்கள் (1-5)""",
        
        "lang_set": "✅ மொழி *தமிழ்* அமைக்கப்பட்டது! 🎉",
        
        "ask_name": "📝 நல்ல தேர்வு!\n\nஉங்கள் பெயர் என்ன?",
        
        "ask_profession": """💼 வணக்கம் {name}!

நீங்கள் என்ன வேலை செய்கிறீர்கள்?

1️⃣ டெலிவரி பார்ட்னர்
2️⃣ கேப்/ஆட்டோ ஓட்டுநர்
3️⃣ தினசரி கூலி
4️⃣ கடைக்காரர்
5️⃣ மாணவர்
6️⃣ இல்லத்தரசி
7️⃣ சம்பளம் பெறுபவர்
8️⃣ ஃப்ரீலான்சர்
9️⃣ மற்றவை

எண் அனுப்புங்கள்""",
        
        "ask_income": "💰 உங்கள் மாத வருமானம் எவ்வளவு?\n\n(எண் மட்டும், எ.கா., 15000)",
        
        "ask_goals": """🎯 உங்கள் இலக்குகள் என்ன?

1️⃣ அவசர நிதி
2️⃣ வீடு
3️⃣ கல்வி
4️⃣ கடன் அடைப்பு
5️⃣ திருமணம்
6️⃣ ஓய்வு
7️⃣ தொழில்
8️⃣ பொது சேமிப்பு

பல தேர்வு செய்யலாம்: "1,3,5\"""",
        
        "ask_savings_target": "📊 மாதம் எவ்வளவு சேமிக்க?\n\nபரிந்துரை: ₹{suggested} (20%)",
        
        "complete": """🎉 *வாழ்த்துக்கள், {name}!*

📊 *உங்கள் திட்டம்:*

💰 வருமானம்: ₹{income}
💾 சேமிப்பு: ₹{savings}/மாதம்
📅 தினசரி பட்ஜெட்: ₹{daily_budget}

{goals_list}

தொடங்குவோம்! 🚀""",
        
        "invalid_choice": "❌ புரியவில்லை. சரியான எண் அனுப்புங்கள்.",
        "invalid_amount": "❌ சரியான தொகை எழுதுங்கள்."
    },
    
    "telugu": {
        "welcome": "🙏 *VittaSaathiకి స్వాగతం!*\n\n1️⃣-8️⃣ భాష ఎంచుకోండి",
        "lang_set": "✅ భాష *తెలుగు* సెట్ చేయబడింది! 🎉",
        "ask_name": "📝 మీ పేరు ఏమిటి?",
        "ask_profession": "💼 {name}, మీరు ఏమి చేస్తారు?\n1️⃣-9️⃣",
        "ask_income": "💰 మీ నెలవారీ ఆదాయం? (సంఖ్య మాత్రమే)",
        "ask_goals": "🎯 మీ లక్ష్యాలు?\n1️⃣-8️⃣ (ఉదా: 1,3,5)",
        "ask_savings_target": "📊 నెలకు ఎంత పొదుపు చేయాలనుకుంటున్నారు?",
        "complete": "🎉 *{name}, సిద్ధం!*\n\n💰 ₹{income}\n💾 ₹{savings}/నెల\n📅 ₹{daily_budget}/రోజు\n\n{goals_list}",
        "invalid_choice": "❌ అర్థం కాలేదు.",
        "invalid_amount": "❌ సరైన మొత్తం వ్రాయండి."
    },
    
    "kannada": {
        "welcome": "🙏 *VittaSaathiಗೆ ಸ್ವಾಗತ!*\n\n1️⃣-8️⃣ ಭಾಷೆ",
        "lang_set": "✅ ಭಾಷೆ *ಕನ್ನಡ*! 🎉",
        "ask_name": "📝 ನಿಮ್ಮ ಹೆಸರು ಏನು?",
        "ask_profession": "💼 {name}, ನಿಮ್ಮ ಕೆಲಸ?\n1️⃣-9️⃣",
        "ask_income": "💰 ಮಾಸಿಕ ಆದಾಯ? (ಸಂಖ್ಯೆ)",
        "ask_goals": "🎯 ನಿಮ್ಮ ಗುರಿಗಳು?\n1️⃣-8️⃣",
        "ask_savings_target": "📊 ತಿಂಗಳಿಗೆ ಎಷ್ಟು ಉಳಿತಾಯ?",
        "complete": "🎉 *{name}!*\n💰 ₹{income}\n💾 ₹{savings}/ತಿಂಗಳು\n📅 ₹{daily_budget}/ದಿನ",
        "invalid_choice": "❌ ಅರ್ಥವಾಗಲಿಲ್ಲ.",
        "invalid_amount": "❌ ಸರಿಯಾದ ಮೊತ್ತ ಬರೆಯಿರಿ."
    }
}

# Profession mapping
PROFESSIONS = {
    "1": "Delivery Partner",
    "2": "Cab/Auto Driver", 
    "3": "Daily Wage Worker",
    "4": "Shopkeeper",
    "5": "Student",
    "6": "Homemaker",
    "7": "Salaried Employee",
    "8": "Freelancer",
    "9": "Other"
}

PROFESSIONS_HINDI = {
    "1": "डिलीवरी पार्टनर",
    "2": "कैब/ऑटो ड्राइवर",
    "3": "दैनिक मजदूर",
    "4": "दुकानदार",
    "5": "छात्र",
    "6": "गृहिणी",
    "7": "नौकरीपेशा",
    "8": "फ्रीलांसर",
    "9": "अन्य"
}

# Goals mapping
GOALS = {
    "1": {"en": "Emergency Fund", "hi": "इमरजेंसी फंड", "emoji": "🏦"},
    "2": {"en": "House/Down Payment", "hi": "घर के लिए बचत", "emoji": "🏠"},
    "3": {"en": "Education", "hi": "शिक्षा", "emoji": "📚"},
    "4": {"en": "Pay off Debt", "hi": "कर्ज चुकाना", "emoji": "💳"},
    "5": {"en": "Marriage", "hi": "शादी", "emoji": "💒"},
    "6": {"en": "Retirement", "hi": "रिटायरमेंट", "emoji": "👴"},
    "7": {"en": "Start Business", "hi": "बिजनेस", "emoji": "🏪"},
    "8": {"en": "General Savings", "hi": "सामान्य बचत", "emoji": "💰"}
}

# Language code mapping - accepts both numbers AND text
LANGUAGE_MAP = {
    # Numbers
    "1": "english",
    "2": "hindi", 
    "3": "tamil",
    "4": "telugu",
    "5": "kannada",
    "6": "malayalam",
    "7": "marathi",
    "8": "bengali",
    # English text
    "english": "english",
    "eng": "english",
    "en": "english",
    "hindi": "hindi",
    "हिंदी": "hindi",
    "हिन्दी": "hindi",
    "tamil": "tamil",
    "தமிழ்": "tamil",
    "telugu": "telugu",
    "తెలుగు": "telugu",
    "kannada": "kannada",
    "ಕನ್ನಡ": "kannada",
    "malayalam": "malayalam",
    "മലയാളം": "malayalam",
    "marathi": "marathi",
    "मराठी": "marathi",
    "bengali": "bengali",
    "বাংলা": "bengali",
    "bangla": "bengali"
}


class SmartOnboardingService:
    """Handles multi-step onboarding with personalized plans"""
    
    def __init__(self, user_repo):
        self.user_repo = user_repo
    
    def get_message(self, key: str, language: str = "english", **kwargs) -> str:
        """Get message in specified language with variable substitution"""
        lang = language if language in ONBOARDING_MESSAGES else "english"
        messages = ONBOARDING_MESSAGES.get(lang, ONBOARDING_MESSAGES["english"])
        template = messages.get(key, ONBOARDING_MESSAGES["english"].get(key, ""))
        
        try:
            return template.format(**kwargs)
        except KeyError:
            return template
    
    def parse_number(self, text: str) -> Optional[int]:
        """Extract number from text - handles 25k, 25000, 25,000 formats"""
        text = text.lower().strip()
        
        # Handle "k" suffix (25k = 25000)
        k_match = re.search(r'(\d+)\s*k\b', text)
        if k_match:
            return int(k_match.group(1)) * 1000
        
        # Handle "lakh" or "lac" (1 lakh = 100000)
        lakh_match = re.search(r'(\d+)\s*(?:lakh|lac)\b', text)
        if lakh_match:
            return int(lakh_match.group(1)) * 100000
        
        # Remove currency symbols, commas, etc.
        cleaned = re.sub(r'[₹,\s]', '', text)
        numbers = re.findall(r'\d+', cleaned)
        if numbers:
            return int(numbers[0])
        return None
    
    def parse_goals(self, text: str) -> List[str]:
        """Parse goal selections from user input - accepts TEXT like 'emergency fund, house'"""
        text = text.lower()
        goals = []
        
        # Goal keywords mapping
        goal_keywords = {
            "1": ["1", "emergency", "fund", "backup", "rainy day"],
            "2": ["2", "house", "home", "property", "flat", "apartment", "down payment"],
            "3": ["3", "education", "study", "college", "school", "course", "learn"],
            "4": ["4", "debt", "loan", "emi", "pay off", "credit card"],
            "5": ["5", "marriage", "wedding", "shaadi", "விவாகம்"],
            "6": ["6", "retirement", "retire", "pension", "old age"],
            "7": ["7", "business", "startup", "shop", "venture", "entrepreneur"],
            "8": ["8", "savings", "save", "general", "money"]
        }
        
        for goal_id, keywords in goal_keywords.items():
            if any(kw in text for kw in keywords):
                goals.append(goal_id)
        
        # If no text match, try numbers
        if not goals:
            numbers = re.findall(r'[1-8]', text)
            goals = list(set(numbers))
        
        return goals[:5]  # Max 5 goals
    
    def format_goals_list(self, goal_ids: List[str], language: str = "english") -> str:
        """Format goals as a readable list"""
        lang_key = "hi" if language == "hindi" else "en"
        lines = []
        for gid in goal_ids:
            if gid in GOALS:
                goal = GOALS[gid]
                lines.append(f"{goal['emoji']} {goal[lang_key]}")
        return "\n".join(lines) if lines else "General Savings"
    
    def calculate_daily_budget(self, income: int, savings_target: int) -> int:
        """Calculate daily spending budget"""
        monthly_spending = income - savings_target
        return max(100, monthly_spending // 30)
    
    def create_personalized_plan(self, user: dict) -> dict:
        """Create a personalized financial plan based on user data"""
        income = user.get("monthly_income", 20000)
        goals = user.get("financial_goals", ["8"])
        savings_target = user.get("savings_target", int(income * 0.2))
        
        daily_budget = self.calculate_daily_budget(income, savings_target)
        savings_percent = round((savings_target / income) * 100) if income > 0 else 20
        
        # Primary goal is the first one
        primary_goal_id = goals[0] if goals else "8"
        lang = user.get("preferred_language", "english")
        lang_key = "hi" if lang == "hindi" else "en"
        primary_goal = GOALS.get(primary_goal_id, GOALS["8"])[lang_key]
        
        return {
            "income": income,
            "savings_target": savings_target,
            "daily_budget": daily_budget,
            "savings_percent": savings_percent,
            "primary_goal": primary_goal,
            "goals": goals,
            "goals_formatted": self.format_goals_list(goals, lang)
        }
    
    def process_onboarding(self, phone: str, message: str, user: dict) -> dict:
        """Process onboarding message and return response"""
        
        step = user.get("onboarding_step", "language")
        language = user.get("preferred_language", "english")
        
        # Step 1: Language selection
        if step == "language" or step == "language_selection":
            lang_input = message.strip().lower()
            selected_lang = LANGUAGE_MAP.get(lang_input)
            
            if selected_lang:
                self.user_repo.update_user(phone, {
                    "preferred_language": selected_lang,
                    "language": selected_lang,
                    "onboarding_step": "name"
                })
                return {
                    "text": self.get_message("lang_set", selected_lang) + "\n\n" + 
                            self.get_message("ask_name", selected_lang),
                    "step": "name"
                }
            else:
                return {
                    "text": self.get_message("invalid_choice", language),
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
                    "text": self.get_message("ask_profession", language, name=name),
                    "step": "profession"
                }
            else:
                return {
                    "text": self.get_message("ask_name", language),
                    "step": "name"
                }
        
        # Step 3: Profession - Accept BOTH text and numbers
        elif step == "profession":
            prof_input = message.strip().lower()
            profession = None
            
            # First check if it's a number (1-9)
            if prof_input in PROFESSIONS:
                profession = PROFESSIONS[prof_input]
            else:
                # Accept text input - map common professions
                profession_keywords = {
                    "student": "Student",
                    "housewife": "Homemaker", 
                    "homemaker": "Homemaker",
                    "teacher": "Salaried Employee",
                    "doctor": "Salaried Employee",
                    "engineer": "Salaried Employee",
                    "it": "Salaried Employee",
                    "software": "Salaried Employee",
                    "employee": "Salaried Employee",
                    "salaried": "Salaried Employee",
                    "driver": "Cab/Auto Driver",
                    "delivery": "Delivery Partner",
                    "zomato": "Delivery Partner",
                    "swiggy": "Delivery Partner",
                    "uber": "Cab/Auto Driver",
                    "ola": "Cab/Auto Driver",
                    "shop": "Shopkeeper",
                    "business": "Shopkeeper",
                    "freelance": "Freelancer",
                    "freelancer": "Freelancer",
                    "self-employed": "Freelancer",
                    "daily wage": "Daily Wage Worker",
                    "labour": "Daily Wage Worker",
                    "worker": "Daily Wage Worker",
                    "other": "Other"
                }
                
                # Check if any keyword matches
                for keyword, prof_value in profession_keywords.items():
                    if keyword in prof_input:
                        profession = prof_value
                        break
                
                # If still no match, accept any text as custom profession
                if not profession and len(prof_input) >= 2:
                    profession = message.strip().title()  # Capitalize properly
            
            if profession:
                self.user_repo.update_user(phone, {
                    "profession": profession,
                    "profession_type": profession.lower().replace(" ", "_"),
                    "onboarding_step": "income"
                })
                return {
                    "text": self.get_message("ask_income", language),
                    "step": "income"
                }
            else:
                name = user.get("name", "Friend")
                return {
                    "text": self.get_message("ask_profession", language, name=name),
                    "step": "profession"
                }
        
        # Step 4: Monthly Income
        elif step == "income":
            income = self.parse_number(message)
            if income and income >= 1000:
                self.user_repo.update_user(phone, {
                    "monthly_income": income,
                    "onboarding_step": "goals"
                })
                return {
                    "text": self.get_message("ask_goals", language),
                    "step": "goals"
                }
            else:
                return {
                    "text": self.get_message("invalid_amount", language),
                    "step": "income"
                }
        
        # Step 5: Financial Goals
        elif step == "goals":
            goals = self.parse_goals(message)
            if goals:
                self.user_repo.update_user(phone, {
                    "financial_goals": goals,
                    "onboarding_step": "savings_target"
                })
                income = user.get("monthly_income", 20000)
                suggested = int(income * 0.2)
                return {
                    "text": self.get_message("ask_savings_target", language, 
                                             income=f"{income:,}", suggested=f"{suggested:,}"),
                    "step": "savings_target"
                }
            else:
                return {
                    "text": self.get_message("ask_goals", language),
                    "step": "goals"
                }
        
        # Step 6: Savings Target - FINAL
        elif step == "savings_target":
            savings = self.parse_number(message)
            income = user.get("monthly_income", 20000)
            
            if not savings:
                savings = int(income * 0.2)  # Default to 20%
            
            # Update user with final data
            self.user_repo.update_user(phone, {
                "savings_target": savings,
                "monthly_budget": income - savings,
                "daily_budget": (income - savings) // 30,
                "onboarding_step": "completed",
                "onboarding_complete": True,
                "onboarding_date": datetime.now().isoformat()
            })
            
            # Get updated user for plan
            updated_user = self.user_repo.get_user(phone)
            plan = self.create_personalized_plan(updated_user)
            
            return {
                "text": self.get_message("complete", language,
                    name=updated_user.get("name", "Friend"),
                    income=f"{plan['income']:,}",
                    savings=f"{plan['savings_target']:,}",
                    percent=plan['savings_percent'],
                    daily_budget=f"{plan['daily_budget']:,}",
                    primary_goal=plan['primary_goal'],
                    goals_list=plan['goals_formatted']
                ),
                "step": "completed",
                "plan": plan
            }
        
        # Default - restart
        else:
            return {
                "text": self.get_message("welcome", "english"),
                "step": "language"
            }


# Create global instance
smart_onboarding = None

def get_smart_onboarding(user_repo):
    global smart_onboarding
    if smart_onboarding is None:
        smart_onboarding = SmartOnboardingService(user_repo)
    return smart_onboarding
