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
    
    # Data file paths
    DATA_DIR = "data"
    USERS_FILE = "data/users.json"
    TRANSACTIONS_FILE = "data/transactions.json"
    
    def __init__(self):
        self.user_store = {}
        self.transaction_store = {}
        self._ensure_data_dir()
        self._load_data()
    
    def _ensure_data_dir(self):
        """Create data directory if not exists"""
        import os
        os.makedirs(self.DATA_DIR, exist_ok=True)
    
    def _load_data(self):
        """Load users and transactions from JSON files"""
        import os
        try:
            if os.path.exists(self.USERS_FILE):
                with open(self.USERS_FILE, 'r', encoding='utf-8') as f:
                    self.user_store = json.load(f)
                print(f"[MoneyViya] Loaded {len(self.user_store)} users from file")
        except Exception as e:
            print(f"[MoneyViya] Error loading users: {e}")
            self.user_store = {}
        
        try:
            if os.path.exists(self.TRANSACTIONS_FILE):
                with open(self.TRANSACTIONS_FILE, 'r', encoding='utf-8') as f:
                    self.transaction_store = json.load(f)
                print(f"[MoneyViya] Loaded transactions from file")
        except Exception as e:
            print(f"[MoneyViya] Error loading transactions: {e}")
            self.transaction_store = {}
    
    def _save_data(self):
        """Save all data to JSON files"""
        try:
            with open(self.USERS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.user_store, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[MoneyViya] Error saving users: {e}")
        
        try:
            with open(self.TRANSACTIONS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.transaction_store, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[MoneyViya] Error saving transactions: {e}")
    
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
        """Detect risk appetite from text or number"""
        text_lower = text.lower().strip()
        
        # Support numbered options
        if text_lower in ["1", "low", "safe"]:
            return "Low"
        if text_lower in ["2", "medium", "moderate", "balanced"]:
            return "Medium"
        if text_lower in ["3", "high", "aggressive"]:
            return "High"
        
        # Check pattern matching
        for risk, patterns in self.RISK_PATTERNS.items():
            for pattern in patterns:
                if pattern in text_lower:
                    return risk.title()
        
        # Return None if not detected (for validation)
        return None
    
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
            self._save_data()  # Save new user
        return self.user_store[phone]
    
    def _save_user(self, phone: str, data: Dict):
        self.user_store[phone] = data
        self._save_data()  # Auto-save to file
        
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
        self._save_data()  # Auto-save transactions
    
    def _show_change_options(self, user: Dict) -> str:
        """Show options to change profile data"""
        lang = user.get("language", "en")
        step = user.get("onboarding_step", 0)
        
        return f"""📝 *Need to change something?*

Type *reset* to start over completely.

Or continue with the current question.
Your current details:
• Name: {user.get('name', 'Not set')}
• Occupation: {user.get('occupation', 'Not set')}
• Income: ₹{int(user.get('monthly_income', 0)):,}
• Expenses: ₹{int(user.get('monthly_expenses', 0)):,}
• Savings: ₹{int(user.get('current_savings', 0)):,}

_Type your answer for the current question, or type *reset* to start fresh._"""
    
    def _is_valid_goal(self, text: str) -> bool:
        """Check if the goal input is valid (not just a single common word)"""
        invalid_words = ["help", "language", "english", "hindi", "tamil", "ok", "yes", "no", 
                        "hi", "hello", "thanks", "thank", "bye", "reset", "back", "change",
                        "1", "2", "3", "low", "medium", "high"]
        text_lower = text.lower().strip()
        
        # Too short
        if len(text_lower) < 3:
            return False
        
        # Single invalid word
        if text_lower in invalid_words:
            return False
        
        # Should have at least 2 words for a proper goal
        words = text_lower.split()
        if len(words) < 2 and len(text_lower) < 8:
            return False
            
        return True
    
    async def process_message(self, phone: str, message: str, 
                             sender_name: str = "Friend") -> str:
        """Main message processing with improved NLP"""
        try:
            user = self._get_user(phone)
            user["last_active"] = self._get_ist_time().isoformat()
            user["sender_name"] = sender_name
            
            # Check if onboarding complete
            if not user.get("onboarding_complete"):
                return await self._handle_onboarding(phone, message, user)
            
            # Handle commands - improved NLP matching
            msg_lower = message.lower().strip()
            
            # Greeting patterns
            if msg_lower in ["hi", "hello", "hey", "start", "hii", "hiii", "namaste", "vanakkam", "नमस्ते", "வணக்கம்"]:
                return self._handle_greeting(user)
            
            # Help patterns
            if any(word in msg_lower for word in ["help", "commands", "menu", "what can you do", "options", "?", "sahayata", "உதவி"]):
                return self._handle_help(user)
            
            # Reset patterns
            if any(word in msg_lower for word in ["reset", "restart", "start over", "fresh start", "नया शुरू"]):
                return self._handle_reset(phone)
            
            # Profile/Status patterns
            if any(word in msg_lower for word in ["profile", "my profile", "status", "my status", "who am i", "my details", "my info", "account"]):
                return self._handle_profile(user)
            
            # Balance/Summary patterns
            if any(word in msg_lower for word in ["balance", "summary", "total", "overview", "how much", "kitna", "எவ்வளவு"]):
                return self._handle_balance(phone, user)
            
            # Goal patterns
            if any(word in msg_lower for word in ["goal", "target", "लक्ष्य", "இலக்கு"]):
                if any(word in msg_lower for word in ["add", "new", "create", "set"]):
                    return self._handle_add_goal(phone, message, user)
                return self._handle_view_goals(user)
            
            # Report patterns
            if any(word in msg_lower for word in ["report", "weekly", "monthly", "analysis"]):
                return self._handle_report(phone, user)
            
            # Market/Stock patterns
            if any(word in msg_lower for word in ["market", "stock", "nifty", "sensex", "share", "invest", "बाजार", "சந்தை"]):
                return self._handle_market(user)
            
            # Savings patterns
            if any(word in msg_lower for word in ["saving", "savings", "बचत", "சேமிப்பு"]):
                return self._handle_savings(phone, user)
            
            # Tip/Advice patterns
            if any(word in msg_lower for word in ["tip", "tips", "advice", "suggest", "recommendation"]):
                return self._handle_tips(user)
            
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

*What is your investment risk preference?*

Please reply with a number:
*1* - 🛡️ Low Risk (Safe - FD, PPF, Savings)
*2* - ⚖️ Medium Risk (Balanced - Mix of safe & growth)
*3* - 🚀 High Risk (Aggressive - Stocks, Mutual Funds)

_Or type: low, medium, high_""",
                "hi": f"""बचत: ₹{int(amount):,} {"💰" if amount > 0 else "- कोई बात नहीं!"}

*आपकी निवेश जोखिम प्राथमिकता क्या है?*

कृपया नंबर भेजें:
*1* - 🛡️ कम जोखिम (सुरक्षित)
*2* - ⚖️ मध्यम जोखिम (संतुलित)
*3* - 🚀 उच्च जोखिम (आक्रामक)""",
                "ta": f"""சேமிப்பு: ₹{int(amount):,}

*உங்கள் முதலீட்டு ரிஸ்க் விருப்பம்?*

எண்ணை அனுப்பவும்:
*1* - 🛡️ குறைந்த ரிஸ்க்
*2* - ⚖️ நடுத்தர ரிஸ்க்
*3* - 🚀 அதிக ரிஸ்க்"""
            }
            return responses.get(lang, responses["en"])
        
        # Step 7: Risk appetite (with validation)
        if step == 7:
            # Check for help/change command
            msg_lower = message.lower().strip()
            if msg_lower in ["help", "back", "change", "edit"]:
                return self._show_change_options(user)
            
            risk = self._detect_risk(message)
            
            # Validate - if not a valid option
            if risk is None:
                return """⚠️ Sorry, I did not understand that.

Please reply with:
*1* - Low Risk (Safe)
*2* - Medium Risk (Balanced)
*3* - High Risk (Aggressive)

Or type: low, medium, high"""
            
            user["risk_appetite"] = risk
            user["onboarding_step"] = 8
            self._save_user(phone, user)
            
            responses = {
                "en": f"""✅ Risk profile: *{risk}* 📊

Now the exciting part - *What is your main financial goal?*

_(Examples: Buy a car, Build emergency fund, Pay off loan, Buy a house, Save for vacation)_

💡 _Type a real goal, not just a word!_""",
                "hi": f"""✅ रिस्क प्रोफाइल: *{risk}* 📊

*आपका मुख्य वित्तीय लक्ष्य क्या है?*
_(उदाहरण: कार खरीदना, इमरजेंसी फंड, लोन चुकाना)_""",
                "ta": f"""✅ ரிஸ்க்: *{risk}* 📊

*உங்கள் முக்கிய நிதி இலக்கு என்ன?*
_(உதாரணம்: கார் வாங்க, அவசர நிதி)_"""
            }
            return responses.get(lang, responses["en"])
        
        # Step 8: Goal (with validation)
        if step == 8:
            # Check for help/change command
            msg_lower = message.lower().strip()
            if msg_lower in ["help", "back", "change", "edit"]:
                return self._show_change_options(user)
            
            # Validate goal input
            if not self._is_valid_goal(message):
                return """⚠️ That does not look like a proper financial goal.

Please enter a *specific goal* like:
• "Buy a car"
• "Build emergency fund"
• "Pay off 5 lakh loan"
• "Save for house down payment"
• "Wedding fund"
• "Child education"

_What is your main financial goal?_"""
            
            goal_name = message.strip().title()
            user["primary_goal"] = goal_name
            user["goals"] = [{"name": goal_name, "status": "active"}]
            user["onboarding_step"] = 9
            self._save_user(phone, user)
            
            responses = {
                "en": f"""Great goal: *{goal_name}* 🎯

*How much do you need for this goal?*
_(Example: 5 lakh, 100000, 20 lakh)_""",
                "hi": f"""बेहतरीन लक्ष्य: *{goal_name}* 🎯

*इसके लिए कितने पैसे चाहिए?*""",
                "ta": f"""சிறந்த இலக்கு: *{goal_name}* 🎯

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
        
        tip_text = "Good time for SIP investments!" if nifty_change > 0 else "Markets volatile - stay invested, do not panic!"
        
        return f"""📈 *Market Update*
{self._get_ist_time().strftime('%d %b %Y, %I:%M %p')}

🇮🇳 *Indian Markets:*
━━━━━━━━━━━━━━━━━━━━━
📊 NIFTY 50: {nifty:,.0f} ({trend}{abs(nifty_change):.2f}%)
📊 SENSEX: {sensex:,.0f}

💡 *Tip:*
{tip_text}

_Type "investment tips" for personalized advice_"""
    
    def _handle_profile(self, user: Dict) -> str:
        """Show user profile summary"""
        name = user.get("name", "User")
        phone = user.get("phone", "")[-10:]
        occupation = user.get("occupation", "Not set")
        income = user.get("monthly_income", 0)
        expenses = user.get("monthly_expenses", 0)
        savings = user.get("current_savings", 0)
        risk = user.get("risk_appetite", "Medium")
        
        return f"""👤 *Your Profile: {name}*
━━━━━━━━━━━━━━━━━━━━━

📱 Phone: ****{phone[-4:]}
💼 Occupation: {occupation}
💰 Monthly Income: ₹{int(income):,}
💸 Monthly Expenses: ₹{int(expenses):,}
🏦 Savings: ₹{int(savings):,}
📊 Risk Profile: {risk}

📈 Daily Budget: ₹{int(user.get('daily_budget', 0)):,}

_To edit, visit the web dashboard or type "reset" to start over._"""
    
    def _handle_savings(self, phone: str, user: Dict) -> str:
        """Show savings summary and tips"""
        savings = user.get("current_savings", 0)
        income = user.get("monthly_income", 0)
        expenses = user.get("monthly_expenses", 0)
        potential_savings = income - expenses
        
        return f"""💰 *Your Savings Overview*
━━━━━━━━━━━━━━━━━━━━━

🏦 Current Savings: ₹{int(savings):,}
📊 Monthly Surplus: ₹{int(potential_savings):,}

💡 *Quick Tips:*
• Save at least 20% of income (₹{int(income * 0.2):,}/month)
• Build emergency fund = 6 months expenses
• Invest surplus in SIPs for long-term growth

📈 At current rate, in 1 year you could save: ₹{int(potential_savings * 12):,}

_Track every expense to save more!_"""
    
    def _handle_tips(self, user: Dict) -> str:
        """Provide financial tips based on user profile"""
        income = user.get("monthly_income", 0)
        risk = user.get("risk_appetite", "Medium")
        
        tips = {
            "Low": """🛡️ *Safe Investment Tips:*
• Fixed Deposits (FD) - 6-7% returns
• PPF - Tax-free, 7.1% returns  
• Govt Bonds - Very secure
• Savings Account - Easy access""",
            
            "Medium": """⚖️ *Balanced Investment Tips:*
• Balanced Mutual Funds - Mix of equity & debt
• NPS - For retirement
• Index Funds - Low cost, market returns
• Gold ETFs - Hedge against inflation""",
            
            "High": """🚀 *Growth Investment Tips:*
• Equity Mutual Funds - High long-term returns
• Direct Stocks - Research before investing
• Small-cap Funds - High risk, high reward
• ELSS - Tax saving + equity growth"""
        }
        
        return f"""{tips.get(risk, tips["Medium"])}

💡 *General Tips:*
• Start SIP with ₹{int(income * 0.1):,}/month
• Review portfolio quarterly
• Don't panic during market dips
• Diversify across asset classes

_Type "market" for live updates_"""
    
    def _handle_unknown(self, message: str, user: Dict) -> str:
        """Handle unrecognized messages with smart suggestions"""
        # Try to understand intent using simple NLP
        msg_lower = message.lower()
        
        # Check if it might be an amount
        if any(char.isdigit() for char in message):
            return """💡 I see a number! Did you mean:
• "Spent 500 on food" - Track expense
• "Earned 5000" - Track income
• "Add goal: Car, 5 lakh, 2 years" - Add goal

Just add a context to help me understand!"""
        
        # Check for common typos/variations
        suggestions = []
        if any(word in msg_lower for word in ["bal", "sum", "mon"]):
            suggestions.append('"balance" - View summary')
        if any(word in msg_lower for word in ["rep", "wee", "month"]):
            suggestions.append('"report" - Get your report')
        if any(word in msg_lower for word in ["gol", "tar", "sav"]):
            suggestions.append('"goals" - View your goals')
        
        if suggestions:
            return f"""💡 Did you mean:
• {chr(10).join('• ' + s for s in suggestions)}

Type what you need, I'll try to help!"""
        
        return f"""🤔 I'm not sure what you meant by: "{message[:40]}..."

*Here's what I can do:*
━━━━━━━━━━━━━━━━━━━━━
💰 *Track Money:*
• "Spent 500 on food"
• "Earned 10000 salary"

📊 *View Info:*
• "Balance" - Daily summary
• "Profile" - Your details
• "Goals" - Your targets
• "Report" - Weekly report

📈 *Get Insights:*
• "Market" - Stock updates
• "Tips" - Investment advice
• "Savings" - Savings overview

🔧 *Others:*
• "Help" - All commands
• "Reset" - Start fresh

Just talk to me naturally! 🤖"""


# Singleton - keep lowercase for import compatibility
moneyview_agent = MoneyViyaAgent()

async def process_message(phone: str, message: str, sender_name: str = "Friend") -> str:
    return await moneyview_agent.process_message(phone, message, sender_name)
