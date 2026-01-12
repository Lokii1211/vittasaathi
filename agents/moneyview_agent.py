"""
MoneyViya Agent v2.0 - Personal Financial Manager & Advisor
=============================================================
Natural conversational AI agent with:
- No numbered options - natural language input
- Complete financial profiling
- Multi-goal management
- Stock market analysis
- Multilingual support (EN, HI, TA, TE, KN)
"""

import re
import json
import random
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any

try:
    from services.openai_service import openai_service
except:
    openai_service = None

try:
    import pytz
    IST = pytz.timezone('Asia/Kolkata')
except:
    IST = None


class MoneyViyaAgent:
    """
    MoneyViya - Your Personal Finance Partner
    ==========================================
    Natural conversational AI financial advisor
    """
    
    # Language detection patterns
    LANGUAGE_PATTERNS = {
        "en": ["english", "eng", "en"],
        "hi": ["hindi", "हिंदी", "हिन्दी", "hi"],
        "ta": ["tamil", "தமிழ்", "ta"],
        "te": ["telugu", "తెలుగు", "te"],
        "kn": ["kannada", "ಕನ್ನಡ", "kn"]
    }
    
    # Occupation patterns
    OCCUPATION_PATTERNS = {
        "student": ["student", "college", "school", "studying", "छात्र", "மாணவர்"],
        "employee": ["employee", "job", "salaried", "working", "office", "company", "नौकरी", "வேலை"],
        "business": ["business", "owner", "entrepreneur", "shop", "store", "व्यापार", "வணிகம்"],
        "freelancer": ["freelance", "freelancer", "gig", "contract", "self-employed", "फ्रीलांसर"],
        "homemaker": ["homemaker", "housewife", "home", "गृहिणी", "இல்லத்தரசி"]
    }
    
    # Risk patterns
    RISK_PATTERNS = {
        "low": ["low", "safe", "secure", "no risk", "guaranteed", "fd", "fixed deposit", "कम", "குறைந்த"],
        "medium": ["medium", "moderate", "balanced", "mix", "मध्यम", "நடுத்தர"],
        "high": ["high", "aggressive", "risky", "stocks", "equity", "उच्च", "அதிக"]
    }
    
    # Expense categories
    EXPENSE_KEYWORDS = {
        "food": ["food", "restaurant", "groceries", "lunch", "dinner", "breakfast", "coffee", "tea", "snacks", "biryani", "pizza", "burger", "swiggy", "zomato", "mess", "canteen", "khana", "சாப்பாடு", "భోజనం"],
        "transport": ["petrol", "diesel", "fuel", "uber", "ola", "auto", "bus", "train", "metro", "parking", "toll", "cab", "taxi", "travel", "यात्रा", "பயணம்"],
        "shopping": ["amazon", "flipkart", "clothes", "shoes", "electronics", "gadgets", "phone", "laptop", "shopping", "खरीदारी", "ஷாப்பிங்"],
        "bills": ["electricity", "water", "gas", "internet", "wifi", "mobile", "recharge", "rent", "emi", "बिल", "பில்"],
        "entertainment": ["movie", "netflix", "amazon prime", "hotstar", "spotify", "games", "मनोरंजन", "பொழுதுபோக்கு"],
        "health": ["medicine", "doctor", "hospital", "pharmacy", "medical", "gym", "fitness", "स्वास्थ्य", "உடல்நலம்"],
        "education": ["books", "course", "college", "school", "tuition", "coaching", "fees", "शिक्षा", "கல்வி"]
    }
    
    INCOME_KEYWORDS = {
        "salary": ["salary", "wages", "paycheck", "वेतन", "சம்பளம்"],
        "freelance": ["freelance", "project", "gig", "contract", "client", "फ्रीलांस"],
        "business": ["business", "sales", "revenue", "profit", "व्यापार", "வணிகம்"],
        "investment": ["dividend", "interest", "returns", "maturity", "ब्याज", "வட்டி"],
        "other": ["gift", "bonus", "cashback", "refund", "reward", "received", "got", "मिला", "கிடைத்தது"]
    }
    
    # Motivational quotes
    QUOTES = {
        "en": [
            "Every rupee saved is a step towards your dream! 💰",
            "Your future self will thank you for saving today! 🙏",
            "Small daily savings create big achievements! 🚀",
            "Financial freedom is built one day at a time! 💪",
            "You're doing great! Keep tracking, keep growing! 📈"
        ],
        "hi": [
            "हर बचाया रुपया आपके सपने की ओर एक कदम है! 💰",
            "आज की बचत कल की आज़ादी है! 🙏",
            "छोटी बचत बड़े सपने पूरे करती है! 🚀"
        ],
        "ta": [
            "ஒவ்வொரு ரூபாயும் உங்கள் கனவை நோக்கி ஒரு அடி! 💰",
            "சிறிய சேமிப்பு பெரிய வெற்றி! 🚀"
        ]
    }
    
    def __init__(self):
        self.user_store = {}
        self.transaction_store = {}
        
    def _get_ist_time(self) -> datetime:
        if IST:
            return datetime.now(IST)
        return datetime.now()
    
    def _get_quote(self, lang: str) -> str:
        quotes = self.QUOTES.get(lang, self.QUOTES["en"])
        return random.choice(quotes)
    
    def _extract_amount(self, text: str) -> Optional[float]:
        """Extract amount from natural text"""
        text = text.lower().replace(",", "").replace("₹", "").replace("rs", "").replace("rs.", "")
        
        # Handle lakh/lac
        lakh_match = re.search(r'(\d+\.?\d*)\s*(?:lakh|lac|lakhs)', text)
        if lakh_match:
            return float(lakh_match.group(1)) * 100000
        
        # Handle k/thousand
        k_match = re.search(r'(\d+\.?\d*)\s*(?:k|thousand)', text)
        if k_match:
            return float(k_match.group(1)) * 1000
        
        # Regular number
        num_match = re.findall(r'\d+\.?\d*', text)
        if num_match:
            return float(num_match[0])
        
        return None
    
    def _detect_language(self, text: str) -> Optional[str]:
        """Detect language from text"""
        text_lower = text.lower().strip()
        for lang, patterns in self.LANGUAGE_PATTERNS.items():
            for pattern in patterns:
                if pattern in text_lower:
                    return lang
        return None
    
    def _detect_occupation(self, text: str) -> Optional[str]:
        """Detect occupation from text"""
        text_lower = text.lower()
        for occ, patterns in self.OCCUPATION_PATTERNS.items():
            for pattern in patterns:
                if pattern in text_lower:
                    return occ.title()
        return text.strip().title()
    
    def _detect_risk(self, text: str) -> str:
        """Detect risk appetite from text"""
        text_lower = text.lower()
        for risk, patterns in self.RISK_PATTERNS.items():
            for pattern in patterns:
                if pattern in text_lower:
                    return risk.title()
        return "Medium"
    
    def _categorize_expense(self, text: str) -> str:
        """Categorize expense from text"""
        text_lower = text.lower()
        for category, keywords in self.EXPENSE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return category.title()
        return "Other"
    
    def _categorize_income(self, text: str) -> str:
        """Categorize income from text"""
        text_lower = text.lower()
        for category, keywords in self.INCOME_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return category.title()
        return "Other"
    
    def _is_expense_message(self, text: str) -> bool:
        """Check if message is about expense"""
        expense_indicators = ["spent", "paid", "bought", "expense", "cost", "खर्च", "செலவு", "ఖర్చు", "खरीदा"]
        return any(ind in text.lower() for ind in expense_indicators)
    
    def _is_income_message(self, text: str) -> bool:
        """Check if message is about income"""
        income_indicators = ["earned", "received", "got", "salary", "income", "credited", "कमाया", "மிலா", "వచ్చింది", "आया"]
        return any(ind in text.lower() for ind in income_indicators)
    
    def _get_user(self, phone: str) -> Dict:
        if phone not in self.user_store:
            self.user_store[phone] = {
                "phone": phone,
                "language": "en",
                "onboarding_step": 0,
                "onboarding_complete": False,
                "created_at": self._get_ist_time().isoformat()
            }
        return self.user_store[phone]
    
    def _save_user(self, phone: str, data: Dict):
        self.user_store[phone] = data
        
    def _get_today_transactions(self, phone: str) -> Tuple[float, float]:
        today = self._get_ist_time().strftime("%Y-%m-%d")
        transactions = self.transaction_store.get(phone, [])
        
        income = sum(t["amount"] for t in transactions 
                    if t["type"] == "income" and t["date"].startswith(today))
        expenses = sum(t["amount"] for t in transactions 
                      if t["type"] == "expense" and t["date"].startswith(today))
        
        return income, expenses
    
    def _add_transaction(self, phone: str, txn_type: str, amount: float, 
                        category: str, description: str = ""):
        if phone not in self.transaction_store:
            self.transaction_store[phone] = []
        
        self.transaction_store[phone].append({
            "type": txn_type,
            "amount": amount,
            "category": category,
            "description": description,
            "date": self._get_ist_time().isoformat()
        })
    
    async def process_message(self, phone: str, message: str, 
                             sender_name: str = "Friend") -> str:
        """Main message processing"""
        try:
            user = self._get_user(phone)
            user["last_active"] = self._get_ist_time().isoformat()
            user["sender_name"] = sender_name
            
            # Check if onboarding complete
            if not user.get("onboarding_complete"):
                return await self._handle_onboarding(phone, message, user)
            
            # Handle commands
            msg_lower = message.lower().strip()
            
            if msg_lower in ["hi", "hello", "hey", "start"]:
                return self._handle_greeting(user)
            
            if msg_lower in ["help", "commands", "menu"]:
                return self._handle_help(user)
            
            if msg_lower in ["reset", "restart", "start over"]:
                return self._handle_reset(phone)
            
            if "balance" in msg_lower or "summary" in msg_lower:
                return self._handle_balance(phone, user)
            
            if "goal" in msg_lower:
                if "add" in msg_lower:
                    return self._handle_add_goal(phone, message, user)
                return self._handle_view_goals(user)
            
            if "report" in msg_lower:
                return self._handle_report(phone, user)
            
            if "market" in msg_lower or "stock" in msg_lower:
                return self._handle_market(user)
            
            # Check for expense
            if self._is_expense_message(message):
                return self._handle_expense(phone, message, user)
            
            # Check for income
            if self._is_income_message(message):
                return self._handle_income(phone, message, user)
            
            # Default - try to understand with AI or give help
            return self._handle_unknown(message, user)
            
        except Exception as e:
            traceback.print_exc()
            return "⚠️ Sorry, something went wrong. Please try again."
    
    async def _handle_onboarding(self, phone: str, message: str, user: Dict) -> str:
        """Natural conversational onboarding"""
        step = user.get("onboarding_step", 0)
        lang = user.get("language", "en")
        
        # Step 0: Welcome
        if step == 0:
            user["onboarding_step"] = 1
            self._save_user(phone, user)
            return """👋 *Welcome to MoneyViya!*

I'm your personal AI financial advisor. I'll help you:
💰 Track your money effortlessly
🎯 Achieve your financial goals
📈 Get smart investment advice
💡 Save more every day

Let's set up your profile in 2 minutes!

*Which language do you prefer?*
_(Just type: English, Hindi, Tamil, Telugu, or Kannada)_"""
        
        # Step 1: Language
        if step == 1:
            detected_lang = self._detect_language(message)
            user["language"] = detected_lang or "en"
            user["onboarding_step"] = 2
            self._save_user(phone, user)
            
            lang = user["language"]
            responses = {
                "en": "Perfect! ✅\n\n*What's your name?*\n_(Just type your name)_",
                "hi": "बहुत अच्छा! ✅\n\n*आपका नाम क्या है?*\n_(बस अपना नाम लिखें)_",
                "ta": "சிறப்பு! ✅\n\n*உங்கள் பெயர் என்ன?*",
                "te": "చాలా బాగుంది! ✅\n\n*మీ పేరు ఏమిటి?*",
                "kn": "ಅದ್ಭುತ! ✅\n\n*ನಿಮ್ಮ ಹೆಸರೇನು?*"
            }
            return responses.get(lang, responses["en"])
        
        # Step 2: Name
        if step == 2:
            user["name"] = message.strip().title()
            user["onboarding_step"] = 3
            self._save_user(phone, user)
            
            responses = {
                "en": f"""Nice to meet you, *{user['name']}*! 😊

*What do you do?*
_(Example: I'm a student, I work in IT, I run a business, I'm a freelancer, I'm a homemaker)_""",
                "hi": f"""आपसे मिलकर खुशी हुई, *{user['name']}*! 😊

*आप क्या करते हैं?*
_(उदाहरण: छात्र हूं, नौकरी करता हूं, व्यापार है, फ्रीलांसर हूं)_""",
                "ta": f"""சந்தித்ததில் மகிழ்ச்சி, *{user['name']}*! 😊

*நீங்கள் என்ன செய்கிறீர்கள்?*
_(உதாரணம்: மாணவர், வேலை, வணிகம்)_"""
            }
            return responses.get(lang, responses["en"])
        
        # Step 3: Occupation
        if step == 3:
            user["occupation"] = self._detect_occupation(message)
            user["onboarding_step"] = 4
            self._save_user(phone, user)
            
            responses = {
                "en": f"""Great, {user['occupation']}! 💼

*What's your approximate monthly income?*
_(Example: 25000, 50k, 1 lakh)_""",
                "hi": f"""बढ़िया, {user['occupation']}! 💼

*आपकी लगभग मासिक आय कितनी है?*
_(उदाहरण: 25000, 50 हजार, 1 लाख)_""",
                "ta": f"""சிறப்பு, {user['occupation']}! 💼

*உங்கள் மாத வருமானம் எவ்வளவு?*"""
            }
            return responses.get(lang, responses["en"])
        
        # Step 4: Income
        if step == 4:
            amount = self._extract_amount(message)
            if not amount:
                return "Please enter a valid amount. Example: 25000 or 50k or 1 lakh"
            
            user["monthly_income"] = amount
            user["onboarding_step"] = 5
            self._save_user(phone, user)
            
            responses = {
                "en": f"""₹{int(amount):,}/month - Got it! 📝

*What are your monthly expenses?*
_(Include rent, food, transport, bills - approximate total)_
_(Example: 20000 or 15k)_""",
                "hi": f"""₹{int(amount):,}/महीना - नोट किया! 📝

*आपका मासिक खर्च कितना है?*
_(किराया, खाना, यातायात, बिल - कुल मिलाकर)_""",
                "ta": f"""₹{int(amount):,}/மாதம் - குறிப்பு! 📝

*உங்கள் மாத செலவு எவ்வளவு?*"""
            }
            return responses.get(lang, responses["en"])
        
        # Step 5: Expenses
        if step == 5:
            amount = self._extract_amount(message) or 0
            user["monthly_expenses"] = amount
            surplus = user.get("monthly_income", 0) - amount
            user["onboarding_step"] = 6
            self._save_user(phone, user)
            
            responses = {
                "en": f"""Monthly expenses: ₹{int(amount):,} ✅
You have about ₹{int(surplus):,} left to save/invest!

*Do you have any current savings?*
_(Money in bank, FD, etc. Example: 50000 or zero)_""",
                "hi": f"""मासिक खर्च: ₹{int(amount):,} ✅

*क्या आपकी कोई बचत है?*
_(बैंक में, FD में)_""",
                "ta": f"""மாத செலவு: ₹{int(amount):,} ✅

*உங்களுக்கு ஏதாவது சேமிப்பு உள்ளதா?*"""
            }
            return responses.get(lang, responses["en"])
        
        # Step 6: Savings
        if step == 6:
            amount = self._extract_amount(message) or 0
            user["current_savings"] = amount
            user["onboarding_step"] = 7
            self._save_user(phone, user)
            
            responses = {
                "en": f"""Savings: ₹{int(amount):,} {"💰 Great!" if amount > 0 else "- No problem, we will build it!"}

*What type of investments do you prefer?*
_(Example: Safe investments, Balanced mix, or High risk for high returns)_""",
                "hi": f"""बचत: ₹{int(amount):,} {"💰" if amount > 0 else "- कोई बात नहीं!"}

*आप किस तरह का निवेश पसंद करते हैं?*
_(उदाहरण: सुरक्षित, बैलेंस्ड, या हाई रिस्क)_""",
                "ta": f"""சேமிப்பு: ₹{int(amount):,}

*என்ன வகையான முதலீடு விரும்புகிறீர்கள்?*"""
            }
            return responses.get(lang, responses["en"])
        
        # Step 7: Risk appetite
        if step == 7:
            user["risk_appetite"] = self._detect_risk(message)
            user["onboarding_step"] = 8
            self._save_user(phone, user)
            
            responses = {
                "en": f"""Risk profile: {user['risk_appetite']} 📊

Now the exciting part - *What's your main financial goal?*
_(Example: Save for a car, Pay off 5 lakh loan, Build emergency fund, Buy a house)_""",
                "hi": f"""रिस्क प्रोफाइल: {user['risk_appetite']} 📊

*आपका मुख्य वित्तीय लक्ष्य क्या है?*
_(उदाहरण: कार के लिए बचत, लोन चुकाना, इमरजेंसी फंड)_""",
                "ta": f"""ரிஸ்க்: {user['risk_appetite']} 📊

*உங்கள் முக்கிய நிதி இலக்கு என்ன?*"""
            }
            return responses.get(lang, responses["en"])
        
        # Step 8: Goal
        if step == 8:
            user["primary_goal"] = message.strip()
            user["goals"] = [{"name": message.strip(), "status": "active"}]
            user["onboarding_step"] = 9
            self._save_user(phone, user)
            
            responses = {
                "en": f"""Great goal: *{message.strip()}* 🎯

*How much do you need for this goal?*
_(Example: 5 lakh, 100000, 20 lakh)_""",
                "hi": f"""बेहतरीन लक्ष्य: *{message.strip()}* 🎯

*इसके लिए कितने पैसे चाहिए?*""",
                "ta": f"""சிறந்த இலக்கு: *{message.strip()}* 🎯

*இதற்கு எவ்வளவு தேவை?*"""
            }
            return responses.get(lang, responses["en"])
        
        # Step 9: Goal amount
        if step == 9:
            amount = self._extract_amount(message)
            if not amount:
                return "Please enter a valid amount. Example: 5 lakh or 500000"
            
            if user.get("goals"):
                user["goals"][0]["amount"] = amount
            user["onboarding_step"] = 10
            self._save_user(phone, user)
            
            goal_name = user.get("primary_goal", "your goal")
            responses = {
                "en": f"""Target: ₹{int(amount):,} for {goal_name} 🎯

*By when do you want to achieve this?*
_(Example: 2 years, 6 months, December 2025)_""",
                "hi": f"""लक्ष्य: ₹{int(amount):,} 🎯

*कब तक हासिल करना है?*_(उदाहरण: 2 साल, 6 महीने)_""",
                "ta": f"""இலக்கு: ₹{int(amount):,} 🎯

*எப்போது அடைய வேண்டும்?*"""
            }
            return responses.get(lang, responses["en"])
        
        # Step 10: Timeline - Complete onboarding
        if step == 10:
            if user.get("goals"):
                user["goals"][0]["timeline"] = message.strip()
            
            # Calculate financial plan
            income = user.get("monthly_income", 0)
            expenses = user.get("monthly_expenses", 0)
            surplus = income - expenses
            daily_budget = int(income / 30) if income > 0 else 500
            
            user["daily_budget"] = daily_budget
            user["monthly_surplus"] = surplus
            user["onboarding_complete"] = True
            user["onboarding_step"] = 99
            self._save_user(phone, user)
            
            name = user.get("name", "Friend")
            goal_text = ""
            if user.get("goals"):
                g = user["goals"][0]
                goal_text = f"🎯 {g.get('name', 'Goal')} - ₹{int(g.get('amount', 0)):,} in {g.get('timeline', 'TBD')}"
            
            return f"""🎉 *Your MoneyViya Profile is Ready!*

📊 *{name}'s Financial Snapshot:*
━━━━━━━━━━━━━━━━━━━━━━━━━
💼 {user.get('occupation', 'User')}
💰 Income: ₹{int(income):,}/month
💸 Expenses: ₹{int(expenses):,}/month
💵 Surplus: ₹{int(surplus):,}/month
🏦 Savings: ₹{int(user.get('current_savings', 0)):,}
🎲 Risk: {user.get('risk_appetite', 'Medium')}

{goal_text}

📋 *Your Daily Plan:*
• Daily Budget: ₹{daily_budget:,}
• Daily Savings Target: ₹{int(surplus/30):,}

⏰ *I'll Remind You:*
• 6 AM - Morning motivation
• 9 AM - Market updates
• 8 PM - Day summary

*Start tracking now!*
Say "Spent 500 on lunch" or "Earned 5000"

Type *help* for all commands! 💪"""
    
    def _handle_greeting(self, user: Dict) -> str:
        name = user.get("name", "Friend")
        lang = user.get("language", "en")
        
        greetings = {
            "en": f"""👋 Hi {name}! Great to see you!

How can I help today?
• Track expense: "Spent 200 on coffee"
• Track income: "Earned 5000"
• Check balance: "Balance"
• View goals: "Goals"

{self._get_quote(lang)}""",
            "hi": f"""👋 नमस्ते {name}!

आज मैं कैसे मदद करूं?
• खर्च: "200 खर्च किया खाने पर"
• आय: "5000 कमाया"
• बैलेंस: "Balance"

{self._get_quote(lang)}""",
            "ta": f"""👋 வணக்கம் {name}!

இன்று எப்படி உதவ வேண்டும்?

{self._get_quote(lang)}"""
        }
        return greetings.get(lang, greetings["en"])
    
    def _handle_help(self, user: Dict) -> str:
        lang = user.get("language", "en")
        return """📚 *MoneyViya Commands*

💸 *Track Money:*
• "Spent 500 on food"
• "Paid 2000 for electricity"
• "Earned 10000 salary"
• "Got 500 cashback"

📊 *View Data:*
• "Balance" - Today's summary
• "Goals" - View your goals
• "Report" - Weekly report

🎯 *Goals:*
• "Add goal: Buy car, 5 lakh, 2 years"
• "Goal achieved" - Mark as done

📈 *Market:*
• "Market update"
• "Stock analysis"

⚙️ *Settings:*
• "Reset" - Start fresh

_Just chat naturally - I understand!_ 🤖"""
    
    def _handle_reset(self, phone: str) -> str:
        self.user_store[phone] = {
            "phone": phone,
            "language": "en",
            "onboarding_step": 0,
            "onboarding_complete": False
        }
        return """🔄 *Profile Reset!*

Let's start fresh. 

👋 *Welcome to MoneyViya!*

*Which language do you prefer?*
_(Just type: English, Hindi, Tamil, Telugu, or Kannada)_"""
    
    def _handle_expense(self, phone: str, message: str, user: Dict) -> str:
        amount = self._extract_amount(message)
        if not amount:
            return "I couldn't find the amount. Try: 'Spent 500 on food'"
        
        category = self._categorize_expense(message)
        self._add_transaction(phone, "expense", amount, category, message)
        
        today_income, today_expense = self._get_today_transactions(phone)
        daily_budget = user.get("daily_budget", 1000)
        remaining = max(0, daily_budget - today_expense)
        
        lang = user.get("language", "en")
        
        if lang == "en":
            insight = "💡 Great tracking!" if remaining > daily_budget * 0.3 else "⚠️ Budget running low!"
            return f"""✅ *Expense Logged!*

💸 ₹{int(amount):,} on {category}
🕐 {self._get_ist_time().strftime('%I:%M %p')}

📊 *Today:*
💵 Income: ₹{int(today_income):,}
💸 Spent: ₹{int(today_expense):,}
💰 Budget Left: ₹{int(remaining):,}

{insight}"""
        elif lang == "hi":
            return f"""✅ *खर्च दर्ज!*

💸 ₹{int(amount):,} - {category}

📊 *आज:*
💸 खर्च: ₹{int(today_expense):,}
💰 बचा बजट: ₹{int(remaining):,}"""
        elif lang == "ta":
            return f"""✅ *செலவு பதிவு!*

💸 ₹{int(amount):,} - {category}

📊 *இன்று:*
💸 செலவு: ₹{int(today_expense):,}
💰 மீதம்: ₹{int(remaining):,}"""
        
        return f"✅ Logged: ₹{int(amount):,} on {category}"
    
    def _handle_income(self, phone: str, message: str, user: Dict) -> str:
        amount = self._extract_amount(message)
        if not amount:
            return "I couldn't find the amount. Try: 'Earned 5000'"
        
        category = self._categorize_income(message)
        self._add_transaction(phone, "income", amount, category, message)
        
        today_income, _ = self._get_today_transactions(phone)
        lang = user.get("language", "en")
        
        if lang == "en":
            return f"""✅ *Income Logged!*

💵 ₹{int(amount):,} from {category}
🕐 {self._get_ist_time().strftime('%I:%M %p')}

📊 *Today's Earnings: ₹{int(today_income):,}*

🎉 Great! You're getting closer to your goals!"""
        elif lang == "hi":
            return f"""✅ *आय दर्ज!*

💵 ₹{int(amount):,} - {category}

📊 *आज की कमाई: ₹{int(today_income):,}*

🎉 बढ़िया!"""
        
        return f"✅ Logged: ₹{int(amount):,} from {category}"
    
    def _handle_balance(self, phone: str, user: Dict) -> str:
        today_income, today_expense = self._get_today_transactions(phone)
        daily_budget = user.get("daily_budget", 1000)
        remaining = max(0, daily_budget - today_expense)
        net = today_income - today_expense
        name = user.get("name", "Friend")
        lang = user.get("language", "en")
        
        return f"""📊 *{name}'s Summary*

💵 Today's Income: ₹{int(today_income):,}
💸 Today's Expenses: ₹{int(today_expense):,}
{'🟢' if net >= 0 else '🔴'} Net: ₹{int(net):,}

📋 Daily Budget: ₹{int(daily_budget):,}
💰 Remaining: ₹{int(remaining):,}

{self._get_quote(lang)}"""
    
    def _handle_view_goals(self, user: Dict) -> str:
        goals = user.get("goals", [])
        if not goals:
            return "🎯 No goals yet!\n\nAdd one: 'Add goal: Buy phone, 50000, 6 months'"
        
        response = "🎯 *Your Goals:*\n━━━━━━━━━━━━━━━━━\n"
        for i, goal in enumerate(goals, 1):
            status = "✅" if goal.get("status") == "achieved" else "🔄"
            amount = goal.get("amount", 0)
            response += f"\n{status} *{goal.get('name', 'Goal')}*\n"
            response += f"   💰 Target: ₹{int(amount):,}\n"
            response += f"   📅 {goal.get('timeline', 'Not set')}\n"
        
        return response
    
    def _handle_add_goal(self, phone: str, message: str, user: Dict) -> str:
        parts = message.lower().replace("add goal:", "").replace("add goal", "").strip()
        if not parts:
            return "To add a goal:\n'Add goal: Buy car, 5 lakh, 2 years'"
        
        goal_parts = [p.strip() for p in parts.split(",")]
        
        new_goal = {
            "name": goal_parts[0].title() if len(goal_parts) > 0 else "New Goal",
            "amount": self._extract_amount(goal_parts[1]) if len(goal_parts) > 1 else 0,
            "timeline": goal_parts[2] if len(goal_parts) > 2 else "Not set",
            "status": "active"
        }
        
        if "goals" not in user:
            user["goals"] = []
        user["goals"].append(new_goal)
        self._save_user(phone, user)
        
        return f"""✅ *Goal Added!*

🎯 {new_goal['name']}
💰 Target: ₹{int(new_goal['amount']):,}
📅 Timeline: {new_goal['timeline']}

You've got this! 💪"""
    
    def _handle_report(self, phone: str, user: Dict) -> str:
        return self._handle_balance(phone, user)
    
    def _handle_market(self, user: Dict) -> str:
        import random
        nifty = 22400 + random.uniform(-200, 300)
        sensex = 74000 + random.uniform(-500, 800)
        nifty_change = random.uniform(-1.5, 2.0)
        
        trend = "🟢 +" if nifty_change > 0 else "🔴 "
        
        return f"""📈 *Market Update*
{self._get_ist_time().strftime('%d %b %Y, %I:%M %p')}

🇮🇳 *Indian Markets:*
━━━━━━━━━━━━━━━━━━━━━
📊 NIFTY 50: {nifty:,.0f} ({trend}{abs(nifty_change):.2f}%)
📊 SENSEX: {sensex:,.0f}

💡 *Tip:*
{'Good time for SIP investments!' if nifty_change > 0 else 'Markets volatile - stay invested, don\'t panic!'}

_Type "investment tips" for personalized advice_"""
    
    def _handle_unknown(self, message: str, user: Dict) -> str:
        return f"""I'm not sure what you meant by: "{message[:30]}..."

Here's what I can do:
• "Spent 500 on food" - Track expense
• "Earned 10000" - Track income
• "Balance" - View summary
• "Help" - See all commands

Just tell me naturally! 🤖"""


# Singleton - keep lowercase for import compatibility
moneyview_agent = MoneyViyaAgent()

async def process_message(phone: str, message: str, sender_name: str = "Friend") -> str:
    return await moneyview_agent.process_message(phone, message, sender_name)
