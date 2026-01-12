"""
MoneyView Agent - Personal Financial Manager & Advisor
========================================================
AI-powered WhatsApp financial agent with:
- Complete onboarding with financial profiling
- Multi-goal management
- Stock market analysis (AlphaVantage)
- Smart budgeting & expense tracking
- Document scanning for receipts
- Multilingual support (EN, HI, TA, TE, KN)
- Personalized financial advice (OpenAI)
"""

import re
import json
import random
import hashlib
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

# Import services
try:
    from services.openai_service import openai_service
except:
    openai_service = None

try:
    import pytz
    IST = pytz.timezone('Asia/Kolkata')
except:
    IST = None


class Language(Enum):
    ENGLISH = "en"
    HINDI = "hi"
    TAMIL = "ta"
    TELUGU = "te"
    KANNADA = "kn"


class Occupation(Enum):
    STUDENT = "student"
    EMPLOYEE = "employee"
    BUSINESS = "business"
    FREELANCER = "freelancer"
    HOMEMAKER = "homemaker"


class RiskAppetite(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class Goal:
    id: str
    name: str
    target_amount: float
    current_amount: float = 0
    deadline: str = ""
    priority: int = 1
    status: str = "active"
    monthly_contribution: float = 0
    created_at: str = ""


@dataclass
class UserProfile:
    phone: str
    name: str = ""
    language: str = "en"
    occupation: str = ""
    monthly_income: float = 0
    fixed_expenses: float = 0
    variable_expenses: float = 0
    current_savings: float = 0
    current_investments: float = 0
    investment_details: Dict = field(default_factory=dict)
    risk_appetite: str = "medium"
    daily_budget: float = 0
    goals: List[Goal] = field(default_factory=list)
    onboarding_step: int = 0
    onboarding_complete: bool = False
    created_at: str = ""
    last_active: str = ""


class MoneyViewAgent:
    """
    MoneyView - Your Personal Finance Partner
    ==========================================
    An AI-powered financial advisor that helps you:
    - Track income & expenses
    - Manage multiple financial goals
    - Get personalized investment advice
    - Receive daily market updates
    - Stay motivated to achieve targets
    """
    
    # Multilingual templates
    TEMPLATES = {
        "en": {
            "welcome": """👋 *Welcome to MoneyView!*

I'm your AI Personal Finance Partner. I'll help you:
💰 Track your money
🎯 Achieve your goals
📈 Invest wisely
💡 Save smarter

Let's set up your profile!

*What language do you prefer?*
1️⃣ English
2️⃣ हिंदी (Hindi)
3️⃣ தமிழ் (Tamil)
4️⃣ తెలుగు (Telugu)
5️⃣ ಕನ್ನಡ (Kannada)""",
            
            "ask_name": "Great choice! ✅\n\n*What should I call you?*\n_(Just type your name)_",
            
            "ask_occupation": """Nice to meet you, *{name}*! 😊

*What do you do?*
1️⃣ Student
2️⃣ Employee/Salaried
3️⃣ Business Owner
4️⃣ Freelancer
5️⃣ Homemaker""",
            
            "ask_income": """Got it, {occupation}! 💼

*What's your approximate monthly income?*
_(Type amount like: 25000 or 50k)_""",
            
            "ask_fixed_expenses": """₹{income:,}/month - noted! 📝

*What are your fixed monthly expenses?*
_(Rent, EMI, subscriptions, bills)_
_(Type amount like: 15000)_""",
            
            "ask_variable_expenses": """Fixed expenses: ₹{fixed:,} ✅

*What about variable expenses?*
_(Food, transport, shopping, entertainment)_""",
            
            "ask_savings": """I see you have about ₹{available:,} left after expenses.

*Do you have any current savings?*
_(Money in savings account)_
_(Type 0 if none)_""",
            
            "ask_investments": """Current savings: ₹{savings:,} 💰

*Any current investments?*
_(FD, Mutual Funds, Stocks, Gold, PPF)_
_(Type 0 if none, or amount like 50000)_""",
            
            "ask_investment_details": """You have ₹{investments:,} invested! 📈

*What type of investments?*
_(Just type: FD, MF, Stocks, Gold, PPF - or skip)_""",
            
            "ask_risk": """Perfect! Now let's understand your risk tolerance.

*What's your investment style?*
1️⃣ Low Risk - I prefer safe investments
2️⃣ Medium Risk - Balanced approach
3️⃣ High Risk - I can take aggressive risks""",
            
            "ask_goal": """Great! Now the exciting part - YOUR GOALS! 🎯

*What's your primary financial goal?*
_(Be specific! Example: Pay off 20 lakh education loan, Buy a car, Build emergency fund)_""",
            
            "ask_goal_amount": """Excellent goal: *{goal}* 🎯

*How much do you need for this?*
_(Type amount like: 500000 or 5 lakh)_""",
            
            "ask_goal_timeline": """Target: ₹{amount:,} for {goal}

*By when do you want to achieve this?*
_(Example: 2 years, 6 months, December 2025)_""",
            
            "ask_more_goals": """Goal set! ✅

*Do you have more goals?*
_(Type another goal or say "no more")_""",
            
            "profile_complete": """🎉 *Your MoneyView Profile is Ready!*

📊 *Financial Snapshot:*
━━━━━━━━━━━━━━━━━━━━━
👤 {name} ({occupation})
💰 Income: ₹{income:,}/month
💸 Expenses: ₹{expenses:,}/month
💵 Monthly Surplus: ₹{surplus:,}
🏦 Savings: ₹{savings:,}
📈 Investments: ₹{investments:,}
🎲 Risk Profile: {risk}

🎯 *Your Goals:*
{goals_list}

📋 *My Plan for You:*
━━━━━━━━━━━━━━━━━━━━━
💸 Daily Budget: ₹{daily_budget:,}
💰 Monthly Savings Target: ₹{monthly_savings:,}
📈 Investment Allocation: ₹{invest_amount:,}

⏰ *I'll Send You:*
• 6 AM - Yesterday's review + Today's targets
• 9 AM - Stock market analysis
• 8 PM - Evening check-in

Type "help" for commands!
Let's achieve your dreams together! 💪""",
            
            "expense_logged": """✅ *Expense Recorded!*

💸 Amount: ₹{amount:,}
📁 Category: {category}
🕐 {time}

📊 *Today So Far:*
💵 Income: ₹{today_income:,}
💸 Spent: ₹{today_expense:,}
💰 Remaining Budget: ₹{remaining:,}

{insight}""",
            
            "income_logged": """✅ *Income Recorded!*

💵 Amount: ₹{amount:,}
📁 Source: {category}
🕐 {time}

📊 *Today's Earnings:*
💵 Total Income: ₹{today_income:,}
🎯 Goal Progress: +₹{amount:,}

{motivation}""",
            
            "morning_briefing": """☀️ *Good Morning, {name}!*

📊 *Yesterday's Summary:*
━━━━━━━━━━━━━━━━━━━━━
💵 Income: ₹{yesterday_income:,}
💸 Expenses: ₹{yesterday_expense:,}
💰 Saved: ₹{saved:,}

🎯 *Today's Targets:*
• Daily Budget: ₹{daily_budget:,}
• Savings Goal: ₹{daily_savings:,}

💪 *Motivation:*
_{quote}_

Have a productive day! 🚀""",
            
            "market_analysis": """📈 *Market Update - {date}*

🇮🇳 *Indian Markets:*
━━━━━━━━━━━━━━━━━━━━━
NIFTY 50: {nifty} ({nifty_change})
SENSEX: {sensex} ({sensex_change})
Bank Nifty: {banknifty} ({banknifty_change})

📊 *Top Performers:*
{top_gainers}

📉 *Top Losers:*
{top_losers}

💡 *My Analysis:*
{analysis}

📌 *Investment Tip:*
{tip}""",
            
            "evening_checkin": """🌙 *Evening Check-in, {name}!*

📊 *Today So Far:*
━━━━━━━━━━━━━━━━━━━━━
💵 Income: ₹{today_income:,}
💸 Expenses: ₹{today_expense:,}
💰 Net: ₹{net:,}

{status_message}

*Any more transactions to add?*
_(Type: "Spent 200 on dinner" or "Earned 500" or "that's all")_""",
            
            "goal_progress": """🎯 *Goal Progress Report*

{goals_progress}

📈 *Overall Progress:*
Total Saved: ₹{total_saved:,}
Target: ₹{total_target:,}
Progress: {progress}%

{motivation}""",
            
            "weekly_report": """📊 *Weekly Report - {name}*
Week: {week_start} to {week_end}
━━━━━━━━━━━━━━━━━━━━━

💵 *Income:*
This Week: ₹{week_income:,}
Last Week: ₹{last_week_income:,}
Change: {income_change}

💸 *Expenses:*
This Week: ₹{week_expense:,}
Last Week: ₹{last_week_expense:,}
Change: {expense_change}

💰 *Savings:*
This Week: ₹{week_savings:,}
Last Week: ₹{last_week_savings:,}
Change: {savings_change}

📈 *Category Breakdown:*
{category_breakdown}

🎯 *Goal Progress:*
{goals_progress}

💡 *AI Insights:*
{insights}

📄 Type "PDF report" for detailed analysis.""",
            
            "help_menu": """📚 *MoneyView Commands*

💸 *Track Money:*
• "Spent 500 on food"
• "Earned 10000 salary"
• "Balance" - View today's summary

🎯 *Goals:*
• "Add goal: Car, 500000, 2 years"
• "Goals" - View all goals
• "Goal achieved: Car" - Mark done

📊 *Reports:*
• "Report" - Weekly summary
• "Monthly report"
• "PDF report"

📈 *Market:*
• "Market update"
• "Stock analysis"

⚙️ *Settings:*
• "Change language"
• "Update income"
• "Reset" - Start fresh

💬 *Or just chat naturally!*
I understand your messages! 🤖"""
        },
        
        "hi": {
            "welcome": """👋 *MoneyView में आपका स्वागत है!*

मैं आपका AI वित्तीय साथी हूं। मैं आपकी मदद करूंगा:
💰 पैसे ट्रैक करने में
🎯 लक्ष्य पूरे करने में
📈 समझदारी से निवेश करने में

*अपनी भाषा चुनें:*
1️⃣ English
2️⃣ हिंदी (Hindi)
3️⃣ தமிழ் (Tamil)
4️⃣ తెలుగు (Telugu)
5️⃣ ಕನ್ನಡ (Kannada)""",
            
            "ask_name": "बढ़िया! ✅\n\n*आपका नाम क्या है?*",
            "ask_occupation": """*{name}* से मिलकर खुशी हुई! 😊

*आप क्या करते हैं?*
1️⃣ छात्र
2️⃣ नौकरी
3️⃣ व्यापार
4️⃣ फ्रीलांसर
5️⃣ गृहिणी""",
            
            "expense_logged": """✅ *खर्च दर्ज!*

💸 राशि: ₹{amount:,}
📁 श्रेणी: {category}

📊 *आज अब तक:*
💵 आय: ₹{today_income:,}
💸 खर्च: ₹{today_expense:,}
💰 बचा बजट: ₹{remaining:,}""",
            
            "income_logged": """✅ *आय दर्ज!*

💵 राशि: ₹{amount:,}
📁 स्रोत: {category}

📊 *आज की कमाई:*
💵 कुल आय: ₹{today_income:,}
🎯 लक्ष्य में जोड़ा: +₹{amount:,}"""
        },
        
        "ta": {
            "welcome": """👋 *MoneyView-க்கு வரவேற்கிறோம்!*

நான் உங்கள் AI நிதி ஆலோசகர். நான் உதவுவேன்:
💰 பணத்தை கண்காணிக்க
🎯 இலக்குகளை அடைய
📈 புத்திசாலித்தனமாக முதலீடு செய்ய

*உங்கள் மொழியை தேர்வு செய்யுங்கள்:*
1️⃣ English
2️⃣ हिंदी (Hindi)
3️⃣ தமிழ் (Tamil)
4️⃣ తెలుగు (Telugu)
5️⃣ ಕನ್ನಡ (Kannada)""",
            
            "ask_name": "சிறப்பு! ✅\n\n*உங்கள் பெயர் என்ன?*",
            
            "expense_logged": """✅ *செலவு பதிவு செய்யப்பட்டது!*

💸 தொகை: ₹{amount:,}
📁 வகை: {category}

📊 *இன்று வரை:*
💵 வருமானம்: ₹{today_income:,}
💸 செலவு: ₹{today_expense:,}
💰 மீதமுள்ள பட்ஜெட்: ₹{remaining:,}""",
            
            "income_logged": """✅ *வருமானம் பதிவு செய்யப்பட்டது!*

💵 தொகை: ₹{amount:,}
📁 ஆதாரம்: {category}

📊 *இன்றைய வருமானம்:*
💵 மொத்த வருமானம்: ₹{today_income:,}"""
        },
        
        "te": {
            "welcome": """👋 *MoneyView కి స్వాగతం!*

నేను మీ AI ఆర్థిక సలహాదారు. నేను సహాయం చేస్తాను:
💰 డబ్బు ట్రాక్ చేయడం
🎯 లక్ష్యాలు సాధించడం
📈 తెలివిగా పెట్టుబడి పెట్టడం

*మీ భాష ఎంచుకోండి:*
1️⃣ English
2️⃣ हिंदी
3️⃣ தமிழ்
4️⃣ తెలుగు
5️⃣ ಕನ್ನಡ""",
            
            "expense_logged": """✅ *ఖర్చు నమోదు!*

💸 మొత్తం: ₹{amount:,}
📁 వర్గం: {category}

📊 *ఈరోజు:*
💸 ఖర్చులు: ₹{today_expense:,}
💰 మిగిలిన బడ్జెట్: ₹{remaining:,}"""
        },
        
        "kn": {
            "welcome": """👋 *MoneyView ಗೆ ಸ್ವಾಗತ!*

ನಾನು ನಿಮ್ಮ AI ಹಣಕಾಸು ಸಲಹೆಗಾರ. ನಾನು ಸಹಾಯ ಮಾಡುತ್ತೇನೆ:
💰 ಹಣ ಟ್ರ್ಯಾಕ್ ಮಾಡಲು
🎯 ಗುರಿಗಳನ್ನು ಸಾಧಿಸಲು
📈 ಬುದ್ಧಿವಂತಿಕೆಯಿಂದ ಹೂಡಿಕೆ ಮಾಡಲು

*ನಿಮ್ಮ ಭಾಷೆ ಆಯ್ಕೆಮಾಡಿ:*
1️⃣ English
2️⃣ हिंदी
3️⃣ தமிழ்
4️⃣ తెలుగు
5️⃣ ಕನ್ನಡ"""
        }
    }
    
    # Motivational quotes
    QUOTES = {
        "en": [
            "A penny saved is a penny earned. 💰",
            "Financial freedom is within your reach! 🚀",
            "Small steps lead to big achievements. 👣",
            "Your future self will thank you. 🙏",
            "Wealth is not about having a lot of money; it's about having options. 💎",
            "Every expense is a choice. Choose wisely! 🎯",
            "Invest in yourself, it pays the best interest. 📚",
            "The best time to start saving was yesterday. The next best time is NOW! ⏰"
        ],
        "hi": [
            "बूंद बूंद से घड़ा भरता है। 💰",
            "आर्थिक स्वतंत्रता आपकी पहुंच में है! 🚀",
            "छोटे कदम बड़ी उपलब्धियों की ओर ले जाते हैं। 👣",
            "बचत करना सबसे अच्छा निवेश है। 🎯"
        ],
        "ta": [
            "சிறு துளி பெரு வெள்ளம். 💰",
            "நிதி சுதந்திரம் உங்கள் கைக்கு எட்டும் தூரத்தில்! 🚀",
            "சிறிய அடிகள் பெரிய வெற்றிகளை அடைய உதவும். 👣"
        ]
    }
    
    # Categories for smart categorization
    EXPENSE_CATEGORIES = {
        "food": ["food", "restaurant", "groceries", "vegetables", "fruits", "snacks", "coffee", "tea", "lunch", "dinner", "breakfast", "biryani", "pizza", "burger", "swiggy", "zomato", "mess", "canteen", "hotel"],
        "transport": ["petrol", "diesel", "fuel", "uber", "ola", "auto", "bus", "train", "metro", "parking", "toll", "cab", "taxi"],
        "shopping": ["amazon", "flipkart", "clothes", "shoes", "electronics", "gadgets", "phone", "laptop", "shopping"],
        "bills": ["electricity", "water", "gas", "internet", "wifi", "broadband", "mobile", "recharge", "rent", "emi"],
        "entertainment": ["movie", "netflix", "amazon prime", "hotstar", "spotify", "games", "subscriptions"],
        "health": ["medicine", "doctor", "hospital", "pharmacy", "medical", "gym", "fitness"],
        "education": ["books", "course", "college", "school", "tuition", "coaching", "fees"]
    }
    
    INCOME_CATEGORIES = {
        "salary": ["salary", "wages", "paycheck"],
        "freelance": ["freelance", "project", "gig", "contract"],
        "business": ["business", "sales", "revenue", "profit", "client"],
        "investment": ["dividend", "interest", "returns", "maturity"],
        "other": ["gift", "bonus", "cashback", "refund", "reward"]
    }
    
    def __init__(self):
        self.user_store = {}  # In-memory store, replace with DB
        self.transaction_store = {}
        self.goal_store = {}
        
    def _get_ist_time(self) -> datetime:
        """Get current IST time"""
        if IST:
            return datetime.now(IST)
        return datetime.now()
    
    def _get_template(self, lang: str, key: str) -> str:
        """Get template for language, fallback to English"""
        if lang in self.TEMPLATES and key in self.TEMPLATES[lang]:
            return self.TEMPLATES[lang][key]
        return self.TEMPLATES["en"].get(key, "")
    
    def _get_quote(self, lang: str) -> str:
        """Get random motivational quote"""
        quotes = self.QUOTES.get(lang, self.QUOTES["en"])
        return random.choice(quotes)
    
    def _extract_amount(self, text: str) -> Optional[float]:
        """Extract amount from text"""
        text = text.lower().replace(",", "")
        
        # Handle lakh/lac
        if "lakh" in text or "lac" in text:
            nums = re.findall(r'(\d+\.?\d*)\s*(?:lakh|lac)', text)
            if nums:
                return float(nums[0]) * 100000
        
        # Handle k
        if "k" in text:
            nums = re.findall(r'(\d+\.?\d*)\s*k', text)
            if nums:
                return float(nums[0]) * 1000
        
        # Handle regular numbers
        nums = re.findall(r'\d+\.?\d*', text)
        if nums:
            return float(nums[0])
        
        return None
    
    def _categorize_expense(self, text: str) -> str:
        """Smart categorize expense using keywords"""
        text_lower = text.lower()
        
        for category, keywords in self.EXPENSE_CATEGORIES.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return category.title()
        
        return "Other"
    
    def _categorize_income(self, text: str) -> str:
        """Smart categorize income"""
        text_lower = text.lower()
        
        for category, keywords in self.INCOME_CATEGORIES.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return category.title()
        
        return "Other"
    
    def _detect_intent(self, message: str) -> str:
        """Detect user intent from message"""
        msg = message.lower().strip()
        
        # Commands
        if msg in ["hi", "hello", "hey", "start", "begin"]:
            return "greeting"
        if msg in ["help", "commands", "menu"]:
            return "help"
        if msg in ["reset", "restart", "start fresh"]:
            return "reset"
        if "balance" in msg or "summary" in msg:
            return "balance"
        if "report" in msg:
            return "report"
        if "goal" in msg:
            if "add" in msg:
                return "add_goal"
            if "achieved" in msg or "done" in msg:
                return "goal_achieved"
            return "view_goals"
        if "market" in msg or "stock" in msg:
            return "market_update"
        if "language" in msg or "change lang" in msg:
            return "change_language"
        
        # Transaction detection
        income_keywords = ["earned", "received", "got", "salary", "income", "credited", "मिला", "आया", "வருமானம்", "ఆదాయం"]
        expense_keywords = ["spent", "paid", "bought", "expense", "खर्च", "செலவு", "ఖర్చు"]
        
        for keyword in income_keywords:
            if keyword in msg:
                return "income"
        
        for keyword in expense_keywords:
            if keyword in msg:
                return "expense"
        
        # Number detection for onboarding
        if msg.isdigit() or self._extract_amount(msg):
            return "number_input"
        
        # Selection (1-5)
        if msg in ["1", "2", "3", "4", "5"]:
            return "selection"
        
        return "chat"
    
    def _get_user(self, phone: str) -> Dict:
        """Get or create user"""
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
        """Save user data"""
        self.user_store[phone] = data
    
    def _get_today_transactions(self, phone: str) -> Tuple[float, float]:
        """Get today's income and expenses"""
        today = self._get_ist_time().strftime("%Y-%m-%d")
        transactions = self.transaction_store.get(phone, [])
        
        income = sum(t["amount"] for t in transactions 
                    if t["type"] == "income" and t["date"].startswith(today))
        expenses = sum(t["amount"] for t in transactions 
                      if t["type"] == "expense" and t["date"].startswith(today))
        
        return income, expenses
    
    def _add_transaction(self, phone: str, txn_type: str, amount: float, 
                        category: str, description: str = ""):
        """Add a transaction"""
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
        """Main message processing entry point"""
        try:
            user = self._get_user(phone)
            user["last_active"] = self._get_ist_time().isoformat()
            user["sender_name"] = sender_name
            
            # Check if onboarding needed
            if not user.get("onboarding_complete"):
                return await self._handle_onboarding(phone, message, user)
            
            # Detect intent
            intent = self._detect_intent(message)
            
            # Route to handlers
            handlers = {
                "greeting": self._handle_greeting,
                "help": self._handle_help,
                "reset": self._handle_reset,
                "expense": self._handle_expense,
                "income": self._handle_income,
                "balance": self._handle_balance,
                "report": self._handle_report,
                "view_goals": self._handle_view_goals,
                "add_goal": self._handle_add_goal,
                "goal_achieved": self._handle_goal_achieved,
                "market_update": self._handle_market_update,
                "change_language": self._handle_change_language,
                "chat": self._handle_chat
            }
            
            handler = handlers.get(intent, self._handle_chat)
            return await handler(phone, message, user)
            
        except Exception as e:
            traceback.print_exc()
            return "⚠️ Sorry, something went wrong. Please try again."
    
    async def _handle_onboarding(self, phone: str, message: str, user: Dict) -> str:
        """Handle onboarding flow"""
        step = user.get("onboarding_step", 0)
        lang = user.get("language", "en")
        
        # Step 0: Welcome & Language
        if step == 0:
            user["onboarding_step"] = 1
            self._save_user(phone, user)
            return self._get_template("en", "welcome")
        
        # Step 1: Language selection
        elif step == 1:
            lang_map = {"1": "en", "2": "hi", "3": "ta", "4": "te", "5": "kn"}
            user["language"] = lang_map.get(message.strip(), "en")
            user["onboarding_step"] = 2
            self._save_user(phone, user)
            return self._get_template(user["language"], "ask_name")
        
        # Step 2: Name
        elif step == 2:
            user["name"] = message.strip().title()
            user["onboarding_step"] = 3
            self._save_user(phone, user)
            return self._get_template(lang, "ask_occupation").format(name=user["name"])
        
        # Step 3: Occupation
        elif step == 3:
            occ_map = {"1": "Student", "2": "Employee", "3": "Business", 
                      "4": "Freelancer", "5": "Homemaker"}
            user["occupation"] = occ_map.get(message.strip(), message.strip().title())
            user["onboarding_step"] = 4
            self._save_user(phone, user)
            return self._get_template(lang, "ask_income").format(occupation=user["occupation"])
        
        # Step 4: Monthly Income
        elif step == 4:
            amount = self._extract_amount(message)
            if amount:
                user["monthly_income"] = amount
                user["onboarding_step"] = 5
                self._save_user(phone, user)
                return self._get_template(lang, "ask_fixed_expenses").format(income=int(amount))
            return "Please enter a valid amount (example: 25000)"
        
        # Step 5: Fixed Expenses
        elif step == 5:
            amount = self._extract_amount(message)
            if amount is not None:
                user["fixed_expenses"] = amount
                user["onboarding_step"] = 6
                self._save_user(phone, user)
                return self._get_template(lang, "ask_variable_expenses").format(fixed=int(amount))
            return "Please enter a valid amount"
        
        # Step 6: Variable Expenses
        elif step == 6:
            amount = self._extract_amount(message)
            if amount is not None:
                user["variable_expenses"] = amount
                total_expenses = user.get("fixed_expenses", 0) + amount
                available = user.get("monthly_income", 0) - total_expenses
                user["onboarding_step"] = 7
                self._save_user(phone, user)
                return self._get_template(lang, "ask_savings").format(available=int(available))
            return "Please enter a valid amount"
        
        # Step 7: Current Savings
        elif step == 7:
            amount = self._extract_amount(message) or 0
            user["current_savings"] = amount
            user["onboarding_step"] = 8
            self._save_user(phone, user)
            return self._get_template(lang, "ask_investments").format(savings=int(amount))
        
        # Step 8: Investments
        elif step == 8:
            amount = self._extract_amount(message) or 0
            user["current_investments"] = amount
            user["onboarding_step"] = 9
            self._save_user(phone, user)
            return self._get_template(lang, "ask_risk")
        
        # Step 9: Risk Appetite
        elif step == 9:
            risk_map = {"1": "Low", "2": "Medium", "3": "High"}
            user["risk_appetite"] = risk_map.get(message.strip(), "Medium")
            user["onboarding_step"] = 10
            self._save_user(phone, user)
            return self._get_template(lang, "ask_goal")
        
        # Step 10: Primary Goal
        elif step == 10:
            user["primary_goal"] = message.strip()
            user["goals"] = [{"name": message.strip(), "status": "pending"}]
            user["onboarding_step"] = 11
            self._save_user(phone, user)
            return self._get_template(lang, "ask_goal_amount").format(goal=message.strip())
        
        # Step 11: Goal Amount
        elif step == 11:
            amount = self._extract_amount(message)
            if amount:
                if user.get("goals"):
                    user["goals"][0]["amount"] = amount
                user["onboarding_step"] = 12
                self._save_user(phone, user)
                return self._get_template(lang, "ask_goal_timeline").format(
                    amount=int(amount), 
                    goal=user.get("primary_goal", "goal")
                )
            return "Please enter a valid amount"
        
        # Step 12: Timeline - Complete Onboarding
        elif step == 12:
            if user.get("goals"):
                user["goals"][0]["timeline"] = message.strip()
            
            # Calculate financial plan
            income = user.get("monthly_income", 0)
            expenses = user.get("fixed_expenses", 0) + user.get("variable_expenses", 0)
            surplus = income - expenses
            daily_budget = int(income / 30) if income > 0 else 500
            
            user["daily_budget"] = daily_budget
            user["monthly_surplus"] = surplus
            user["onboarding_complete"] = True
            user["onboarding_step"] = 99
            self._save_user(phone, user)
            
            # Generate goals list
            goals_list = ""
            if user.get("goals"):
                for i, goal in enumerate(user["goals"], 1):
                    goals_list += f"🎯 {i}. {goal.get('name', 'Goal')} - ₹{int(goal.get('amount', 0)):,}\n"
            
            return self._get_template(lang, "profile_complete").format(
                name=user.get("name", "Friend"),
                occupation=user.get("occupation", "User"),
                income=int(income),
                expenses=int(expenses),
                surplus=int(surplus),
                savings=int(user.get("current_savings", 0)),
                investments=int(user.get("current_investments", 0)),
                risk=user.get("risk_appetite", "Medium"),
                goals_list=goals_list or "No goals set yet",
                daily_budget=daily_budget,
                monthly_savings=int(surplus * 0.3),
                invest_amount=int(surplus * 0.2)
            )
        
        return self._get_template(lang, "welcome")
    
    async def _handle_greeting(self, phone: str, message: str, user: Dict) -> str:
        """Handle greetings"""
        lang = user.get("language", "en")
        name = user.get("name", "Friend")
        
        greetings = {
            "en": f"👋 Hi {name}! How can I help you today?",
            "hi": f"👋 नमस्ते {name}! आज मैं आपकी कैसे मदद कर सकता हूं?",
            "ta": f"👋 வணக்கம் {name}! இன்று நான் எப்படி உதவ வேண்டும்?",
            "te": f"👋 నమస్తే {name}! ఈరోజు నేను ఎలా సహాయం చేయగలను?"
        }
        
        return greetings.get(lang, greetings["en"]) + "\n\nType 'help' for commands."
    
    async def _handle_help(self, phone: str, message: str, user: Dict) -> str:
        """Show help menu"""
        lang = user.get("language", "en")
        return self._get_template(lang, "help_menu")
    
    async def _handle_reset(self, phone: str, message: str, user: Dict) -> str:
        """Reset user data"""
        self.user_store[phone] = {
            "phone": phone,
            "language": "en",
            "onboarding_step": 0,
            "onboarding_complete": False
        }
        return self._get_template("en", "welcome")
    
    async def _handle_expense(self, phone: str, message: str, user: Dict) -> str:
        """Handle expense logging"""
        lang = user.get("language", "en")
        amount = self._extract_amount(message)
        
        if not amount:
            return "I couldn't detect the amount. Please try: 'Spent 500 on food'"
        
        category = self._categorize_expense(message)
        self._add_transaction(phone, "expense", amount, category, message)
        
        today_income, today_expense = self._get_today_transactions(phone)
        daily_budget = user.get("daily_budget", 1000)
        remaining = max(0, daily_budget - today_expense)
        
        # Generate insight
        insights = [
            "💡 Great tracking! Every expense counts.",
            "💡 Keep monitoring - you're doing well!",
            "💡 Smart spenders become wealthy!",
        ]
        if remaining < daily_budget * 0.2:
            insights = ["⚠️ Budget running low - consider limiting more expenses today!"]
        
        return self._get_template(lang, "expense_logged").format(
            amount=int(amount),
            category=category,
            time=self._get_ist_time().strftime("%I:%M %p"),
            today_income=int(today_income),
            today_expense=int(today_expense),
            remaining=int(remaining),
            insight=random.choice(insights)
        )
    
    async def _handle_income(self, phone: str, message: str, user: Dict) -> str:
        """Handle income logging"""
        lang = user.get("language", "en")
        amount = self._extract_amount(message)
        
        if not amount:
            return "I couldn't detect the amount. Please try: 'Earned 5000'"
        
        category = self._categorize_income(message)
        self._add_transaction(phone, "income", amount, category, message)
        
        today_income, _ = self._get_today_transactions(phone)
        
        motivations = [
            "🎉 Excellent! Your income is growing!",
            "💪 Great work! Keep building wealth!",
            "🚀 You're on the path to financial freedom!"
        ]
        
        return self._get_template(lang, "income_logged").format(
            amount=int(amount),
            category=category,
            time=self._get_ist_time().strftime("%I:%M %p"),
            today_income=int(today_income),
            motivation=random.choice(motivations)
        )
    
    async def _handle_balance(self, phone: str, message: str, user: Dict) -> str:
        """Show today's balance summary"""
        lang = user.get("language", "en")
        name = user.get("name", "Friend")
        
        today_income, today_expense = self._get_today_transactions(phone)
        daily_budget = user.get("daily_budget", 1000)
        remaining = max(0, daily_budget - today_expense)
        net = today_income - today_expense
        
        return f"""📊 *{name}'s Summary*

💵 Today's Income: ₹{int(today_income):,}
💸 Today's Expenses: ₹{int(today_expense):,}
💰 Net: ₹{int(net):,}

📋 Daily Budget: ₹{int(daily_budget):,}
💰 Remaining: ₹{int(remaining):,}

{self._get_quote(lang)}"""
    
    async def _handle_report(self, phone: str, message: str, user: Dict) -> str:
        """Generate report"""
        # Placeholder - implement full report generation
        return await self._handle_balance(phone, message, user)
    
    async def _handle_view_goals(self, phone: str, message: str, user: Dict) -> str:
        """View all goals"""
        goals = user.get("goals", [])
        if not goals:
            return "🎯 No goals set yet!\n\nAdd a goal: 'Add goal: Buy Car, 500000, 2 years'"
        
        response = "🎯 *Your Goals:*\n━━━━━━━━━━━━━━━━━\n"
        for i, goal in enumerate(goals, 1):
            status = "✅" if goal.get("status") == "achieved" else "🔄"
            response += f"{status} {i}. {goal.get('name', 'Goal')}\n"
            response += f"   Target: ₹{int(goal.get('amount', 0)):,}\n"
            response += f"   Timeline: {goal.get('timeline', 'Not set')}\n\n"
        
        return response
    
    async def _handle_add_goal(self, phone: str, message: str, user: Dict) -> str:
        """Add a new goal"""
        # Parse: Add goal: Name, Amount, Timeline
        parts = message.lower().replace("add goal:", "").replace("add goal", "").strip()
        
        if not parts:
            return "To add a goal, type:\n'Add goal: Buy Car, 500000, 2 years'"
        
        goal_parts = [p.strip() for p in parts.split(",")]
        
        new_goal = {
            "name": goal_parts[0] if len(goal_parts) > 0 else "New Goal",
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
    
    async def _handle_goal_achieved(self, phone: str, message: str, user: Dict) -> str:
        """Mark goal as achieved"""
        goals = user.get("goals", [])
        if not goals:
            return "No goals to mark as achieved!"
        
        # Mark first active goal as achieved
        for goal in goals:
            if goal.get("status") != "achieved":
                goal["status"] = "achieved"
                self._save_user(phone, user)
                return f"""🎉 *Congratulations!*

You've achieved your goal:
🏆 {goal.get('name', 'Goal')}

This is a huge accomplishment! 
Keep going - the sky's the limit! 🚀"""
        
        return "All goals are already achieved! Time to add new ones! 🎯"
    
    async def _handle_market_update(self, phone: str, message: str, user: Dict) -> str:
        """Get market update - placeholder for AlphaVantage integration"""
        return """📈 *Market Update*

🇮🇳 Indian Markets:
• NIFTY 50: 22,456 (+0.5%)
• SENSEX: 74,125 (+0.4%)
• Bank Nifty: 48,890 (+0.8%)

💡 *Today's Insight:*
Markets are showing positive momentum. 
Consider starting an SIP in index funds!

_Full analysis coming soon with AlphaVantage integration_"""
    
    async def _handle_change_language(self, phone: str, message: str, user: Dict) -> str:
        """Change language"""
        return """*Select your language:*
1️⃣ English
2️⃣ हिंदी (Hindi)
3️⃣ தமிழ் (Tamil)
4️⃣ తెలుగు (Telugu)
5️⃣ ಕನ್ನಡ (Kannada)"""
    
    async def _handle_chat(self, phone: str, message: str, user: Dict) -> str:
        """Handle general chat - use OpenAI for understanding"""
        lang = user.get("language", "en")
        
        # Try OpenAI if available
        if openai_service:
            try:
                system_prompt = f"""You are MoneyView, a friendly AI financial advisor. 
The user speaks {lang}. Their name is {user.get('name', 'Friend')}.
Their monthly income is ₹{user.get('monthly_income', 0):,}.
Their goals: {user.get('goals', [])}.
Be helpful, motivational, and provide financial guidance.
Keep responses concise (under 100 words).
Use emojis appropriately."""
                
                response = await openai_service.chat_completion(
                    system_prompt=system_prompt,
                    user_message=message
                )
                return response
            except:
                pass
        
        # Fallback
        return f"""I understand you said: "{message}"

I'm still learning to understand more complex queries!

Here's what I can help with:
• "Spent 500 on food" - Log expense
• "Earned 10000" - Log income
• "Balance" - View summary
• "Goals" - View your goals
• "Help" - See all commands"""


# Create singleton instance
moneyview_agent = MoneyViewAgent()


# Async wrapper function
async def process_message(phone: str, message: str, sender_name: str = "Friend") -> str:
    """Process incoming WhatsApp message"""
    return await moneyview_agent.process_message(phone, message, sender_name)
