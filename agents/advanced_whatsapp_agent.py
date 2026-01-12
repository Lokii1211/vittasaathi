"""
Advanced WhatsApp Financial Agent v4.0
======================================
Senior-Level AI Agent that serves as the PRIMARY interface for financial management.
Web Dashboard is SECONDARY - only for visualization.

Features:
---------
1. Natural Language Understanding (Multi-language)
2. Context-Aware Conversations
3. Proactive Financial Insights
4. Daily Reminders System
5. OTP Authentication Support
6. Investment Advisory
7. Budget Tracking & Alerts
8. Goal Progress Monitoring
9. Fraud Detection Alerts
10. Family Finance Support

Author: Senior AI Agentic Engineer
"""

import os
import re
import json
import random
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Tuple, Any
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

# Import core services
try:
    from services.nlp_service import nlp_service
    from services.financial_advisor import financial_advisor
    from services.investment_service import investment_service
    from services.openai_service import openai_service
    from database.user_repository import user_repo
    from database.transaction_repository import transaction_repo
    from database.goal_repository import goal_repo
except ImportError as e:
    print(f"Import warning: {e}")


class AdvancedWhatsAppAgent:
    """
    Senior-Level WhatsApp Financial Agent
    Primary interface for all financial operations
    """
    
    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY", "")
        
        # Conversation context storage
        self.conversation_context = {}
        
        # Intent handlers mapping
        self.intent_handlers = {
            "log_expense": self._handle_expense,
            "log_income": self._handle_income,
            "check_balance": self._handle_balance,
            "view_report": self._handle_report,
            "set_goal": self._handle_budget,  # Uses same handler as budget_query
            "investment_advice": self._handle_investment,
            "budget_query": self._handle_budget,
            "help": self._handle_help,
            "greeting": self._handle_greeting,
            "otp_request": self._handle_otp_request,
            "confirmation": self._handle_confirmation,
            "market_update": self._handle_market_update,
        }
        
        # Response templates (Multi-language)
        self.templates = self._load_templates()
        
        # Smart patterns for NLP
        self.smart_patterns = self._load_smart_patterns()
        
    def _load_templates(self) -> Dict:
        """Load response templates for multiple languages"""
        return {
            "en": {
                "welcome": """👋 *Welcome to MoneyViya!*
Your AI Financial Advisor on WhatsApp.

I can help you:
💰 Track expenses & income
📊 Get financial insights
🎯 Set & monitor goals
📈 Investment advice
📋 Generate reports

*Just chat naturally!*
Example: "Spent 500 on groceries" or "How much did I spend this week?"
""",
                "expense_logged": """✅ *Expense Recorded!*

💸 Amount: ₹{amount}
📁 Category: {category}
📅 {date}

💰 Today's Total Spending: ₹{today_total}
📊 Remaining Budget: ₹{remaining}

{tip}""",
                "income_logged": """✅ *Income Recorded!*

💵 Amount: ₹{amount}
📁 Source: {category}
📅 {date}

💰 *Today's Earnings:* ₹{today_income}
🎯 *Goal Progress:* +₹{amount} closer!

{motivation}""",
                "balance_summary": """📊 *Your Financial Summary*

💰 *Current Balance:* ₹{balance}
━━━━━━━━━━━━━━━━━
📈 Income: ₹{income}
📉 Expenses: ₹{expenses}
💵 Savings: ₹{savings}
━━━━━━━━━━━━━━━━━

🎯 Goal: {goal_name}
📊 Progress: {goal_progress}%
📅 Days Left: {days_left}

{insight}""",
                "help_menu": """📱 *MoneyViya Help*

*Quick Commands:*
━━━━━━━━━━━━━━━━━
💸 *Log Expense:* "Spent 200 on food"
💵 *Log Income:* "Earned 5000 from delivery"
📊 *See Balance:* "What's my balance?"
📋 *Report:* "Show weekly report"
🎯 *Goals:* "How's my goal?"
📈 *Invest:* "Investment ideas"
🔐 *Login:* "Send OTP"

*Or just chat naturally!*
I understand context and can help with:
• Budgeting advice
• Savings tips
• Market updates
• Financial planning

Type anything to get started! 💪""",
                "morning_reminder": """☀️ *Good Morning, {name}!*

📅 *Today's Financial Plan:*
━━━━━━━━━━━━━━━━━
💰 Daily Budget: ₹{daily_budget}
🎯 Savings Target: ₹{daily_target}
📊 Yesterday: ₹{yesterday_saved} saved
━━━━━━━━━━━━━━━━━

{motivation}

💡 *Tip:* {daily_tip}

*Track expenses by just texting!*
Example: "Spent 50 on tea" """,
                "evening_checkout": """🌙 *Daily Closing - {date}*

📊 *Today's Summary:*
━━━━━━━━━━━━━━━━━
💵 Income: ₹{income}
💸 Expenses: ₹{expenses}
💰 Net: ₹{net}
━━━━━━━━━━━━━━━━━

{comparison}

🎯 *Goal Progress:*
{progress_bar}
₹{saved}/₹{target} ({progress}%)

{advice}

*Is this complete?* Reply Yes/No
Or add: "Also spent 100 on..."
""",
                "otp_sent": """🔐 *Your MoneyViya Login Code:*

*{otp}*

⏰ Valid for 5 minutes
Do NOT share this with anyone!

Enter this code on the website to access your dashboard.""",
            },
            "hi": {
                "welcome": """👋 *मनीविया में आपका स्वागत है!*
आपका वित्तीय सलाहकार व्हाट्सएप पर।

मैं मदद कर सकता हूं:
💰 खर्च और आय ट्रैक करें
📊 वित्तीय जानकारी पाएं
🎯 लक्ष्य निर्धारित करें

*बस प्राकृतिक रूप से चैट करें!*
उदाहरण: "किराने पर 500 खर्च किए" या "इस हफ्ते कितना खर्च हुआ?"
""",
                "expense_logged": """✅ *खर्च दर्ज!*

💸 राशि: ₹{amount}
📁 श्रेणी: {category}
📅 {date}

💰 आज का कुल खर्च: ₹{today_total}""",
                "income_logged": """✅ *आय दर्ज!*

💵 राशि: ₹{amount}
📁 स्रोत: {category}
📅 {date}

💰 *आज की कमाई:* ₹{today_income}
🎯 *लक्ष्य प्रगति:* +₹{amount} और करीब!

{motivation}""",
            },
            "ta": {
                "welcome": """👋 *மணிவியாவுக்கு வரவேற்கிறோம்!*
உங்கள் நிதி ஆலோசகர் வாட்ஸ்அப்பில்.

நான் உதவ முடியும்:
💰 செலவு மற்றும் வருமானம் கண்காணிக்க
📊 நிதி நுண்ணறிவு பெற
🎯 இலக்குகளை அமைக்க

*இயல்பாக அரட்டை அடிக்கவும்!*
""",
                "expense_logged": """✅ *செலவு பதிவு செய்யப்பட்டது!*

💸 தொகை: ₹{amount}
📁 வகை: {category}
📅 {date}

💰 இன்றைய மொத்த செலவு: ₹{today_total}
📊 மீதமுள்ள பட்ஜெட்: ₹{remaining}

{tip}""",
                "income_logged": """✅ *வருமானம் பதிவு செய்யப்பட்டது!*

💵 தொகை: ₹{amount}
📁 ஆதாரம்: {category}
📅 {date}

💰 *இன்றைய வருமானம்:* ₹{today_income}
🎯 *இலக்கு முன்னேற்றம்:* +₹{amount} நெருக்கமாக!

{motivation}""",
                "balance_summary": """📊 *உங்கள் நிதி சுருக்கம்*

💰 *தற்போதைய இருப்பு:* ₹{balance}
━━━━━━━━━━━━━━━━━
📈 வருமானம்: ₹{income}
📉 செலவுகள்: ₹{expenses}
💵 சேமிப்பு: ₹{savings}

{insight}""",
                "help_menu": """📱 *மணிவியா உதவி*

*விரைவான கட்டளைகள்:*
━━━━━━━━━━━━━━━━━
💸 *செலவு:* "உணவில் 200 செலவழித்தேன்"
💵 *வருமானம்:* "டெலிவரியில் 5000 சம்பாதித்தேன்"
📊 *இருப்பு:* "என் இருப்பு என்ன?"
📋 *அறிக்கை:* "வாராந்திர அறிக்கை காட்டு"

*அல்லது இயல்பாக அரட்டை அடிக்கவும்!* 💪""",
            }
        }

    def _load_smart_patterns(self) -> Dict:
        """Load smart NLP patterns for intent detection"""
        return {
            "expense": {
                "patterns": [
                    r"spent|paid|खर्च|செலவு|ఖర్చు|buy|bought|पैसे दिए",
                    r"(\d+)\s*(rs|rupees|₹|रुपये)?",
                ],
                "categories": {
                    "food": ["food", "खाना", "சாப்பாடு", "tea", "chai", "lunch", "dinner", "breakfast", "snack", "biryani", "pizza"],
                    "transport": ["auto", "bus", "uber", "ola", "petrol", "diesel", "यात्रा", "பயணம்", "train", "metro"],
                    "bills": ["bill", "recharge", "electricity", "बिजली", "phone", "internet", "rent", "किराया"],
                    "shopping": ["amazon", "flipkart", "clothes", "kapde", "shopping", "mall"],
                    "medical": ["medicine", "doctor", "hospital", "दवाई", "மருந்து"],
                    "entertainment": ["movie", "netflix", "game", "मनोरंजन"],
                }
            },
            "income": {
                "patterns": [
                    r"earned|received|got|मिला|கிடைத்தது|salary|income|kamai|வருமானம்",
                ],
                "categories": {
                    "salary": ["salary", "तनख्वाह", "சம்பளம்"],
                    "gig": ["delivery", "uber", "ola", "swiggy", "zomato", "dunzo"],
                    "business": ["business", "shop", "दुकान", "கடை", "sale"],
                    "freelance": ["freelance", "project", "client"],
                    "other": ["gift", "refund", "bonus", "cashback"],
                }
            },
            "query": {
                "balance": [r"balance|बैलेंस|இருப்பு|how much|kitna|எவ்வளவு"],
                "report": [r"report|summary|रिपोर्ट|அறிக்கை|weekly|monthly"],
                "goal": [r"goal|target|लक्ष्य|இலக்கு|progress"],
            },
            "investment": [r"invest|stock|mutual fund|gold|sip|fd|market|share|शेयर"],
            "greeting": [r"^(hi|hello|hey|hola|नमस्ते|வணக்கம்|హాయ్)$"],
            "help": [r"help|menu|मदद|உதவி|సహాయం|what can you do"],
            "confirmation": {
                "positive": [r"^(yes|yeah|yep|हां|ஆம்|అవును|ok|okay|done|confirm|correct|sahi)$"],
                "negative": [r"^(no|nope|नहीं|இல்லை|కాదు|wait|add more|wrong|galat)$"],
            },
            "otp": [r"otp|login|code|verification|वेरिफिकेशन|உறுதிப்படுத்தல்"],
        }

    async def process_message(self, phone: str, message: str, user_data: Dict = None) -> str:
        """
        Main entry point for processing WhatsApp messages
        """
        import pytz
        ist = pytz.timezone('Asia/Kolkata')
        
        print(f"[AdvancedAgent] Processing message from {phone}: {message[:50]}...")
        
        # Load user data if not provided
        if user_data is None:
            user_data = user_repo.get_user(phone) or {}
        
        # Ensure user exists
        if not user_data.get("phone"):
            user_repo.ensure_user(phone)
            user_data = user_repo.get_user(phone) or {"phone": phone}
            user_data["onboarding_step"] = 0
            user_repo.update_user(phone, user_data)
        
        # Store phone in user_data for handlers
        user_data["phone"] = phone
        
        # SMART COMMAND HANDLING
        msg_lower = message.strip().lower()
        current_lang = user_data.get("language")
        valid_langs = ["en", "hi", "ta", "te"]
        
        # Reset/Start Fresh commands
        if msg_lower in ["reset", "start fresh", "start over", "restart", "नया शुरू", "மீண்டும் தொடங்கு"]:
            user_data["onboarding_step"] = 0
            user_data["onboarding_complete"] = False
            user_data["language"] = None
            user_repo.update_user(phone, user_data)
            return """🔄 *Starting Fresh!*

Let's begin again...

👋 *Welcome to VittaSaathi!*
Your Personal AI Financial Advisor 💰

🌐 *Please select your language:*

1️⃣ English
2️⃣ हिंदी (Hindi)
3️⃣ தமிழ் (Tamil)
4️⃣ తెలుగు (Telugu)

_(Reply with 1, 2, 3, or 4)_"""
        
        # Language change command
        if msg_lower in ["language", "change language", "lang", "भाषा", "மொழி"]:
            user_data["onboarding_step"] = 0
            user_data["language"] = None
            user_repo.update_user(phone, user_data)
            return """🌐 *Change Language*

Please select your preferred language:

1️⃣ English
2️⃣ हिंदी (Hindi)
3️⃣ தமிழ் (Tamil)
4️⃣ తెలుగు (Telugu)

_(Reply with 1, 2, 3, or 4)_"""
        
        # Quick language selection (direct)
        if msg_lower in ["english", "hindi", "tamil", "telugu"]:
            lang_map = {"english": "en", "hindi": "hi", "tamil": "ta", "telugu": "te"}
            user_data["language"] = lang_map.get(msg_lower, "en")
            user_repo.update_user(phone, user_data)
            confirms = {"en": "Language set to English! ✅", "hi": "भाषा हिंदी में सेट है! ✅", 
                       "ta": "மொழி தமிழில் அமைக்கப்பட்டது! ✅", "te": "భాష తెలుగులో సెట్ చేయబడింది! ✅"}
            return confirms.get(user_data["language"], "Language updated! ✅") + "\n\nHow can I help you today?"
        
        # Force language selection if not set or invalid
        if not current_lang or current_lang not in valid_langs:
            # Check if user is selecting language (1, 2, 3, 4)
            if msg_lower in ["1", "2", "3", "4"]:
                lang_map = {"1": "en", "2": "hi", "3": "ta", "4": "te"}
                user_data["language"] = lang_map.get(msg_lower, "en")
                user_data["onboarding_step"] = 2  # Move to name step
                user_repo.update_user(phone, user_data)
                greetings = {"en": "Great!", "hi": "बहुत अच्छा!", "ta": "நல்லது!", "te": "చాలా బాగుంది!"}
                return f"""{greetings.get(user_data["language"], "Great!")} ✅

*What should I call you?*
_(Just type your name)_"""
            else:
                # Show language selection
                return """👋 *Welcome to VittaSaathi!*
Your Personal AI Financial Advisor 💰

🌐 *Please select your language:*

1️⃣ English
2️⃣ हिंदी (Hindi)
3️⃣ தமிழ் (Tamil)
4️⃣ తెలుగు (Telugu)

_(Reply with 1, 2, 3, or 4)_"""
        
        # Get conversation context
        context = self._get_context(phone)
        context["language"] = user_data.get("language", "en")
        context["timestamp"] = datetime.now(ist).isoformat()
        
        # Check if onboarding is needed
        if not user_data.get("onboarding_complete"):
            return self._handle_onboarding(phone, message, user_data, context)
        
        # Detect intent using smart NLP
        intent, entities = self._detect_intent(message, context)
        
        print(f"[AdvancedAgent] Intent: {intent}, Entities: {entities}")
        
        # Update context
        context["last_message"] = message
        context["last_intent"] = intent
        context["last_entities"] = entities
        
        # Route to handler
        handler = self.intent_handlers.get(intent, self._handle_fallback)
        response = handler(message, user_data, entities, context)
        
        # Save context
        context["last_response"] = response
        self._save_context(phone, context)
        
        return response
    
    def _detect_language(self, text: str, default: str = "en") -> str:
        """Detect language from text"""
        # Hindi detection
        if re.search(r'[\u0900-\u097F]', text):
            return "hi"
        # Tamil detection
        if re.search(r'[\u0B80-\u0BFF]', text):
            return "ta"
        # Telugu detection
        if re.search(r'[\u0C00-\u0C7F]', text):
            return "te"
        return default
    
    def _detect_intent(self, message: str, context: Dict) -> Tuple[str, Dict]:
        """
        Advanced intent detection with context awareness
        
        Returns:
            Tuple of (intent_name, extracted_entities)
        """
        text = message.lower().strip()
        entities = {}
        
        # Check for OTP request first (high priority)
        if any(re.search(p, text) for p in self.smart_patterns["otp"]):
            return "otp_request", entities
        
        # Check for greeting
        if any(re.search(p, text) for p in self.smart_patterns["greeting"]):
            return "greeting", entities
            
        # Check for help
        if any(re.search(p, text) for p in self.smart_patterns["help"]):
            return "help", entities
        
        # Check for confirmation (context-dependent)
        if context.get("awaiting_confirmation"):
            if any(re.search(p, text) for p in self.smart_patterns["confirmation"]["positive"]):
                return "confirmation", {"type": "positive"}
            if any(re.search(p, text) for p in self.smart_patterns["confirmation"]["negative"]):
                return "confirmation", {"type": "negative"}
        
        # Check for investment queries
        if any(re.search(p, text) for p in self.smart_patterns["investment"]):
            return "investment_advice", entities
        
        # Check for INCOME logging FIRST (important: before expense!)
        # Income keywords: earned, received, got, income, salary, etc.
        income_keywords = ["earn", "income", "received", "got paid", "salary", "kamai", "mila", "मिला", "கிடைத்தது", "వచ్చింది"]
        if any(kw in text for kw in income_keywords):
            entities["amount"] = self._extract_amount(text)
            entities["category"] = self._extract_category(text, "income")
            if entities["amount"]:
                return "log_income", entities
        
        # Then check income patterns
        income_patterns = self.smart_patterns["income"]["patterns"]
        if any(re.search(p, text) for p in income_patterns):
            entities["amount"] = self._extract_amount(text)
            entities["category"] = self._extract_category(text, "income")
            if entities["amount"]:
                return "log_income", entities
        
        # Check for expense logging (after income check)
        expense_keywords = ["spent", "paid", "bought", "खर्च", "செலவு", "ఖర్చు", "kharcha", "kharach"]
        if any(kw in text for kw in expense_keywords):
            entities["amount"] = self._extract_amount(text)
            entities["category"] = self._extract_category(text, "expense")
            if entities["amount"]:
                return "log_expense", entities
        
        # Then check expense patterns
        expense_patterns = self.smart_patterns["expense"]["patterns"]
        if any(re.search(p, text) for p in expense_patterns):
            # But NOT if it matches income keywords
            if not any(kw in text for kw in income_keywords):
                entities["amount"] = self._extract_amount(text)
                entities["category"] = self._extract_category(text, "expense")
                if entities["amount"]:
                    return "log_expense", entities
        
        # Check for balance/report queries
        for query_type, patterns in self.smart_patterns["query"].items():
            if any(re.search(p, text) for p in patterns):
                if query_type == "balance":
                    return "check_balance", entities
                elif query_type == "report":
                    return "view_report", entities
                elif query_type == "goal":
                    return "budget_query", entities
        
        # Try AI-based intent detection as fallback
        return self._ai_detect_intent(text, context)
    
    def _extract_amount(self, text: str) -> Optional[int]:
        """Extract monetary amount from text"""
        text = text.lower().replace(",", "").replace("₹", "").replace("rs", "").replace("rupees", "")
        
        # Handle 'k' and 'lakh' shortcuts
        if match := re.search(r'(\d+(?:\.\d+)?)\s*k\b', text):
            return int(float(match.group(1)) * 1000)
        if match := re.search(r'(\d+(?:\.\d+)?)\s*(?:l|lakh)\b', text):
            return int(float(match.group(1)) * 100000)
        
        # Standard number extraction
        numbers = re.findall(r'\b(\d+)\b', text)
        if numbers:
            return int(numbers[0])
        return None
    
    def _extract_category(self, text: str, tx_type: str = "expense") -> str:
        """Extract category from text"""
        text = text.lower()
        categories = self.smart_patterns[tx_type]["categories"]
        
        for category, keywords in categories.items():
            if any(kw in text for kw in keywords):
                return category
        return "other"
    
    def _ai_detect_intent(self, text: str, context: Dict) -> Tuple[str, Dict]:
        """Use AI/LLM for complex intent detection"""
        
        # Use OpenAI Service if available
        if openai_service.is_available():
            result = openai_service.understand_message(text, context.get("language", "english"))
            intent = result.get("intent", "").lower()
            
            # Map OpenAI intents to internal intents
            intent_map = {
                "expense_entry": "log_expense",
                "income_entry": "log_income",
                "balance_query": "check_balance",
                "report_query": "view_report",
                "greeting": "greeting",
                "investment_query": "investment_advice"
            }
            
            if mapped_intent := intent_map.get(intent):
                entities = {
                    "amount": result.get("amount"),
                    "category": result.get("category", "other"),
                    "description": result.get("description", text)
                }
                return mapped_intent, entities
        
        # Fallback to smart heuristics
        if amount := self._extract_amount(text):
            # Check context for hints
            last_intent = context.get("last_intent", "")
            last_response = context.get("last_response", "").lower()
            
            if "expense" in last_intent or "spent" in last_response:
                return "log_expense", {"amount": amount, "category": "other"}
            elif "income" in last_intent or "earned" in last_response:
                return "log_income", {"amount": amount, "category": "other"}
        
        return "fallback", {}
    
    def _get_context(self, phone: str) -> Dict:
        """Get conversation context for user"""
        if phone not in self.conversation_context:
            self.conversation_context[phone] = {
                "messages": [],
                "last_intent": None,
                "awaiting_confirmation": False,
            }
        return self.conversation_context[phone]
    
    def _save_context(self, phone: str, context: Dict):
        """Save conversation context"""
        self.conversation_context[phone] = context
    
    # =================== INTENT HANDLERS ===================
    
    def _handle_expense(self, message: str, user_data: Dict, entities: Dict, context: Dict) -> str:
        """Handle expense logging"""
        import pytz
        ist = pytz.timezone('Asia/Kolkata')
        
        amount = entities.get("amount", 0)
        category = entities.get("category", "other")
        
        if not amount:
            return "💸 I couldn't find the amount. Please say like: 'Spent 200 on food'"
        
        # Log the expense with IST time
        phone = user_data.get("phone")
        ist_now = datetime.now(ist)
        try:
            transaction_repo.add_transaction(
                user_id=phone,
                amount=amount,
                txn_type="expense",
                category=category,
                description=message
            )
        except Exception as e:
            print(f"Error logging expense: {e}")
            import traceback
            traceback.print_exc()
        
        # Get today's total (accumulated)
        today_total = self._get_today_expenses(phone)
        daily_budget = user_data.get("daily_budget", 500)
        remaining = max(0, daily_budget - today_total)
        
        # Spending tip
        tips = [
            "💡 Pack lunch tomorrow to save ₹100!",
            "💡 Compare prices before buying!",
            "💡 Small savings add up over time!",
            "💡 Track every expense for better insights!",
        ]
        
        lang = user_data.get("language", "en")
        template = self.templates.get(lang, self.templates["en"])["expense_logged"]
        
        return template.format(
            amount=amount,
            category=category.title(),
            date=ist_now.strftime("%d %b, %I:%M %p"),
            today_total=today_total,
            remaining=remaining,
            tip=random.choice(tips)
        )
    
    def _handle_income(self, message: str, user_data: Dict, entities: Dict, context: Dict) -> str:
        """Handle income logging"""
        amount = entities.get("amount", 0)
        category = entities.get("category", "other")
        
        if not amount:
            return "💵 I couldn't find the amount. Please say like: 'Earned 5000 from delivery'"
        
        # Use IST for everything
        import pytz
        ist = pytz.timezone('Asia/Kolkata')
        ist_now = datetime.now(ist)
        
        # Log the income WITH IST timestamp
        phone = user_data.get("phone")
        try:
            transaction_repo.add_transaction(
                user_id=phone,
                amount=amount,
                txn_type="income",
                category=category,
                description=message
            )
            print(f"[Income] Logged ₹{amount} for {phone} at {ist_now.strftime('%I:%M %p IST')}")
        except Exception as e:
            print(f"Error logging income: {e}")
            import traceback
            traceback.print_exc()
        
        # Get today's total income (accumulated) - INCLUDING this transaction
        today_income = self._get_today_income(phone)
        
        motivations = [
            "🔥 Great work! Keep earning!",
            "💪 Every rupee counts towards your goal!",
            "🌟 You're making progress!",
            "🎯 Stay focused on your target!",
        ]
        
        lang = user_data.get("language", "en")
        template = self.templates.get(lang, self.templates["en"])["income_logged"]
        
        return template.format(
            amount=amount,
            category=category.title(),
            date=ist_now.strftime("%d %b, %I:%M %p"),
            today_income=today_income,
            motivation=random.choice(motivations)
        )
    
    def _handle_balance(self, message: str, user_data: Dict, entities: Dict, context: Dict) -> str:
        """Handle balance/summary query"""
        phone = user_data.get("phone")
        
        # Get financial data
        income = self._get_month_income(phone)
        expenses = self._get_month_expenses(phone)
        balance = income - expenses
        savings = max(0, balance)
        
        # Goal info
        goal = self._get_active_goal(phone)
        goal_name = goal.get("name", "Financial Freedom") if goal else "No Goal Set"
        goal_progress = self._get_goal_progress(phone)
        days_left = goal.get("days_left", 365) if goal else 0
        
        # Generate insight
        insights = [
            "💡 You're doing well! Consider increasing SIP by ₹500.",
            "💡 Food expenses are high. Try meal prepping!",
            "💡 Great savings rate! Keep it up!",
            "💡 Review subscriptions to find savings.",
        ]
        
        lang = user_data.get("language", "en")
        template = self.templates.get(lang, self.templates["en"]).get("balance_summary", self.templates["en"]["balance_summary"])
        
        return template.format(
            balance=balance,
            income=income,
            expenses=expenses,
            savings=savings,
            goal_name=goal_name,
            goal_progress=goal_progress,
            days_left=days_left,
            insight=random.choice(insights)
        )
    
    def _handle_report(self, message: str, user_data: Dict, entities: Dict, context: Dict) -> str:
        """Handle report generation request"""
        phone = user_data.get("phone")
        name = user_data.get("name", "Friend")
        lang = user_data.get("language", "en")
        
        # Determine report type
        report_type = "weekly"  # default
        if "month" in message.lower():
            report_type = "monthly"
        
        # Get data
        income = self._get_month_income(phone)
        expenses = self._get_month_expenses(phone)
        savings = income - expenses
        
        # Category breakdown (simplified)
        categories = self._get_category_breakdown(phone)
        
        # Report titles by language
        titles = {
            "en": f"📊 *Weekly Report for {name}*",
            "ta": f"📊 *{name} வாராந்திர அறிக்கை*",
            "hi": f"📊 *{name} साप्ताहिक रिपोर्ट*",
            "te": f"📊 *{name} వారపు నివేదిక*"
        }
        
        # Labels by language
        labels = {
            "en": {"income": "Total Income", "expenses": "Total Expenses", "savings": "Net Savings", 
                   "categories": "Category Breakdown", "insight": "AI Insight", "pdf": "Get PDF"},
            "ta": {"income": "மொத்த வருமானம்", "expenses": "மொத்த செலவுகள்", "savings": "நிகர சேமிப்பு",
                   "categories": "வகை பிரிப்பு", "insight": "AI நுண்ணறிவு", "pdf": "PDF பெறுங்கள்"},
            "hi": {"income": "कुल आय", "expenses": "कुल खर्च", "savings": "शुद्ध बचत",
                   "categories": "श्रेणी विवरण", "insight": "AI अंतर्दृष्टि", "pdf": "PDF प्राप्त करें"},
            "te": {"income": "మొత్తం ఆదాయం", "expenses": "మొత్తం ఖర్చులు", "savings": "నికర పొదుపు",
                   "categories": "వర్గాల వివరణ", "insight": "AI అంతర్దృష్టి", "pdf": "PDF పొందండి"}
        }
        
        l = labels.get(lang, labels["en"])
        
        report = f"""{titles.get(lang, titles["en"])}
━━━━━━━━━━━━━━━━━━━━

💵 *{l['income']}:* ₹{income:,}
💸 *{l['expenses']}:* ₹{expenses:,}
💰 *{l['savings']}:* ₹{savings:,}

📈 *{l['categories']}:*
"""
        if not categories:
            no_expense = {
                "en": "No expenses recorded this period.",
                "ta": "இந்த காலகட்டத்தில் செலவுகள் பதிவு செய்யப்படவில்லை.",
                "hi": "इस अवधि में कोई खर्च दर्ज नहीं।",
                "te": "ఈ కాలంలో ఖర్చులు నమోదు కాలేదు."
            }
            report += no_expense.get(lang, no_expense["en"]) + "\n"
        else:
            for cat, amount in categories.items():
                emoji = {"food": "🍽️", "transport": "🚗", "bills": "📱", "shopping": "🛍️", "other": "📦"}.get(cat, "📦")
                report += f"{emoji} {cat.title()}: ₹{amount:,}\n"
        
        insights = {
            "en": "Focus on reducing food expenses to hit your savings goal faster!",
            "ta": "உங்கள் சேமிப்பு இலக்கை விரைவாக அடைய உணவு செலவுகளை குறைக்க கவனம் செலுத்துங்கள்!",
            "hi": "अपने बचत लक्ष्य को तेजी से हासिल करने के लिए खाने के खर्च कम करें!",
            "te": "మీ సేవింగ్స్ లక్ష్యాన్ని త్వరగా సాధించడానికి ఆహార ఖర్చులను తగ్గించండి!"
        }
        
        pdf_msg = {
            "en": 'Type "PDF report" for detailed analysis.',
            "ta": '"PDF அறிக்கை" என டைப் செய்யுங்கள் விரிவான பகுப்பாய்விற்கு.',
            "hi": 'विस्तृत विश्लेषण के लिए "PDF रिपोर्ट" टाइप करें।',
            "te": 'వివరమైన విశ్లేషణ కోసం "PDF నివేదిక" టైప్ చేయండి.'
        }
        
        report += f"""
💡 *{l['insight']}:* {insights.get(lang, insights["en"])}

📄 *{l['pdf']}:* {pdf_msg.get(lang, pdf_msg["en"])}"""
        
        return report


    def _get_ist_time(self):
        """Get current time in IST"""
        import pytz
        return datetime.now(pytz.timezone('Asia/Kolkata'))

    
    def _handle_investment(self, message: str, user_data: Dict, entities: Dict, context: Dict) -> str:
        """Handle investment advice request"""
        try:
            # Check if amount mentioned
            amount = self._extract_amount(message)
            
            if amount and ("invest" in message.lower() or "plan" in message.lower()):
                return investment_service.get_portfolio_plan(amount)
            
            return investment_service.get_market_analysis()
        except Exception as e:
            print(f"Investment error: {e}")
            return """📈 *Investment Ideas*

Based on your profile, consider:

1️⃣ *SIP in Index Funds* - ₹500/month minimum
   Low risk, good for beginners

2️⃣ *Digital Gold* - Start with ₹100
   Safe, easy to liquidate

3️⃣ *PPF/EPF* - Tax saving
   Long term, guaranteed returns

💡 *Tip:* Start small, stay consistent!

Type "Invest 10000" for a detailed portfolio plan."""
    
    def _handle_budget(self, message: str, user_data: Dict, entities: Dict, context: Dict) -> str:
        """Handle budget/goal queries"""
        phone = user_data.get("phone")
        goal = self._get_active_goal(phone)
        
        if not goal:
            return """🎯 *No Goal Set Yet!*

Let's set a financial goal. What do you want to achieve?

Examples:
• "Save 1 lakh for bike"
• "Build emergency fund of 50000"
• "Clear 20000 loan in 6 months"

Just tell me your goal!"""
        
        goal_name = goal.get("name", "Savings Goal")
        target = goal.get("target_amount", 100000)
        progress = self._get_goal_progress(phone)
        saved = int(target * progress / 100)
        days_left = goal.get("days_left", 365)
        daily_target = int((target - saved) / max(1, days_left))
        
        # Progress bar
        filled = int(progress / 10)
        progress_bar = "█" * filled + "░" * (10 - filled)
        
        return f"""🎯 *Goal: {goal_name}*

📊 *Progress:*
{progress_bar} {progress}%

💰 Saved: ₹{saved:,} / ₹{target:,}
📅 Days Left: {days_left}
📈 Daily Target: ₹{daily_target}

💡 *To stay on track:*
• Save ₹{daily_target} daily
• Reduce non-essential spending
• Find extra income opportunities

Keep going! You got this! 💪"""
    
    def _handle_help(self, message: str, user_data: Dict, entities: Dict, context: Dict) -> str:
        """Handle help request"""
        lang = user_data.get("language", "en")
        return self.templates.get(lang, self.templates["en"]).get("help_menu", """📱 *VittaSaathi Help*

*Quick Commands:*
━━━━━━━━━━━━━━━━━
💸 *Log Expense:* "Spent 200 on food"
💵 *Log Income:* "Earned 5000 from delivery"
📊 *See Balance:* "What's my balance?"
📋 *Report:* "Show report"
🎯 *Goals:* "How's my goal?"
📈 *Invest:* "Investment ideas"
📊 *Market:* "Today's market"
🔐 *Login:* "Send OTP"
🌐 *Language:* "Change language"

*Just type naturally, I understand!* 🤖""")
    
    def _handle_greeting(self, message: str, user_data: Dict, entities: Dict, context: Dict) -> str:
        """Handle greeting"""
        name = user_data.get("name", "Friend")
        hour = datetime.now().hour
        
        if hour < 12:
            greeting = "Good Morning"
        elif hour < 17:
            greeting = "Good Afternoon"
        else:
            greeting = "Good Evening"
        
        return f"""👋 *{greeting}, {name}!*

How can I help you today?

Quick options:
💰 Check balance
📊 See report
💸 Log expense
📈 Investment ideas

Or just tell me what you need!"""
    
    def _handle_otp_request(self, message: str, user_data: Dict, entities: Dict, context: Dict) -> str:
        """Handle OTP generation for web login"""
        import random
        import time
        
        otp = str(random.randint(100000, 999999))
        phone = user_data.get("phone")
        
        # Store OTP in user data
        user_data["temp_otp"] = otp
        user_data["otp_expiry"] = time.time() + 300  # 5 minutes
        
        try:
            user_repo.update_user(phone, user_data)
            print(f"[OTP] Generated {otp} for {phone}, stored in user_repo")
        except Exception as e:
            print(f"Error storing OTP: {e}")
        
        lang = user_data.get("language", "en")
        template = self.templates.get(lang, self.templates["en"]).get("otp_sent", """🔐 *Your Login Code:*

*{otp}*

⏰ Valid for 5 minutes
Do NOT share this with anyone!

Enter this code on the website to access your dashboard.""")
        
        return template.format(otp=otp)
    
    def _handle_confirmation(self, message: str, user_data: Dict, entities: Dict, context: Dict) -> str:
        """Handle yes/no confirmations"""
        confirm_type = entities.get("type", "positive")
        
        if confirm_type == "positive":
            context["awaiting_confirmation"] = False
            return """✅ *Great!* I've updated your records.

Your day is complete! 🌙

📊 Tomorrow I'll send your morning summary.
💤 Good night!"""
        else:
            context["awaiting_confirmation"] = False
            return """📝 *No problem!*

What else would you like to add?

Just tell me:
• "Spent 100 on snacks"
• "Earned 500 from work"

Or type "done" when finished."""
    
    def _handle_market_update(self, message: str, user_data: Dict, entities: Dict, context: Dict) -> str:
        """Handle market update request"""
        try:
            return investment_service.get_market_analysis()
        except:
            return """📈 *Market Update*

🟢 *Nifty 50:* Stable
🟡 *Sensex:* Slight dip
🟢 *Gold:* Rising trend

💡 *Today's Tip:*
"In volatile markets, SIP is your best friend!"

Type "invest" for personalized advice."""
    
    def _handle_fallback(self, message: str, user_data: Dict, entities: Dict, context: Dict) -> str:
        """Handle unrecognized messages using AI for smart conversation"""
        
        # Try to understand with context
        name = user_data.get("name", "Friend")
        lang = user_data.get("language", "english")
        
        # Use OpenAI if available for smart chat
        if openai_service.is_available():
            try:
                import requests
                # Simple chat completion for general queries
                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.openai_key}", "Content-Type": "application/json"},
                    json={
                        "model": "gpt-3.5-turbo",
                        "messages": [
                            {"role": "system", "content": f"You are MoneyViya, a helpful financial advisor on WhatsApp. The user's name is {name}. Keep responses short, friendly, and helpful. Language: {lang}. If valid financial advice is asked, give it. If off-topic, nicely guide back to finance."},
                            {"role": "user", "content": message}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 150
                    },
                    timeout=10
                )
                if response.ok:
                    return response.json()["choices"][0]["message"]["content"].strip()
            except Exception as e:
                print(f"OpenAI Chat Error: {e}")

        # Check if it might be a number (for expense/income)
        if amount := self._extract_amount(message):
            context["pending_amount"] = amount
            return f"""💰 Got ₹{amount}

Is this an:
1️⃣ Expense (spent)
2️⃣ Income (earned)

Just reply with 1 or 2, or say "spent on food" / "earned from work\""""
        
        # Generic helpful response
        return f"""🤔 *Hi {name}!*

I'm not fully sure, but I can help you with your finances!

Try these:
💸 "Spent 200 on food"
💵 "Earned 5000"
📊 "Show balance"
📈 "Investment advice"
❓ "Help"

Or ask me any financial question!"""
    
    # =================== ONBOARDING ===================
    
    def _handle_onboarding(self, phone: str, message: str, user_data: Dict, context: Dict) -> str:
        """Handle user onboarding flow"""
        step = user_data.get("onboarding_step", 0)
        
        # Normalize step
        if isinstance(step, str):
            step = 0
            user_data["onboarding_step"] = 0
        
        if step == 0:  # Language selection
            user_data["onboarding_step"] = 1
            user_repo.update_user(phone, user_data)
            return """👋 *Welcome to VittaSaathi!*
Your Personal AI Financial Advisor 💰

🌐 *Please select your language:*

1️⃣ English
2️⃣ हिंदी (Hindi)
3️⃣ தமிழ் (Tamil)
4️⃣ తెలుగు (Telugu)

_(Reply with 1, 2, 3, or 4)_"""
        
        elif step == 1:  # Got language
            lang_map = {"1": "en", "2": "hi", "3": "ta", "4": "te", 
                       "english": "en", "hindi": "hi", "tamil": "ta", "telugu": "te"}
            lang = lang_map.get(message.strip().lower(), "en")
            user_data["language"] = lang
            user_data["onboarding_step"] = 2
            user_repo.update_user(phone, user_data)
            
            # Multilingual confirmation and name prompt
            responses = {
                "en": """Great! ✅

*What should I call you?*
_(Just type your name)_""",
                "hi": """बहुत अच्छा! ✅

*मैं आपको क्या बुलाऊं?*
_(अपना नाम टाइप करें)_""",
                "ta": """நல்லது! ✅

*உங்களை நான் என்ன அழைக்கட்டும்?*
_(உங்கள் பெயரை டைப் செய்யுங்கள்)_""",
                "te": """చాలా బాగుంది! ✅

*నేను మిమ్మల్ని ఏమని పిలవాలి?*
_(మీ పేరు టైప్ చేయండి)_"""
            }
            return responses.get(lang, responses["en"])
        
        elif step == 2:  # Got name
            user_data["name"] = message.strip().title()
            user_data["onboarding_step"] = 3
            user_repo.update_user(phone, user_data)
            lang = user_data.get("language", "en")
            name = user_data["name"]
            
            responses = {
                "en": f"""Nice to meet you, *{name}*! 😊

*What do you do for work?*
_(e.g., Student, Delivery Partner, Business Owner, Homemaker)_""",
                "hi": f"""आपसे मिलकर अच्छा लगा, *{name}*! 😊

*आप क्या काम करते हैं?*
_(जैसे: छात्र, डिलीवरी पार्टनर, व्यापारी, गृहिणी)_""",
                "ta": f"""சந்திப்பதில் மகிழ்ச்சி, *{name}*! 😊

*நீங்கள் என்ன வேலை செய்கிறீர்கள்?*
_(உ.ம், மாணவர், டெலிவரி பார்ட்னர், வணிக உரிமையாளர், இல்லத்தரசி)_""",
                "te": f"""కలవడం ఆనందం, *{name}*! 😊

*మీరు ఏ పని చేస్తారు?*
_(ఉ.దా., విద్యార్థి, డెలివరీ పార్ట్నర్, వ్యాపార యజమాని, గృహిణి)_"""
            }
            return responses.get(lang, responses["en"])
        
        elif step == 3:  # Got occupation
            user_data["occupation"] = message.strip().title()
            user_data["onboarding_step"] = 4
            user_repo.update_user(phone, user_data)
            lang = user_data.get("language", "en")
            
            responses = {
                "en": """Got it! 👍

*What's your approximate monthly income?*
_(Just type amount, e.g., 25000 or 25k)_""",
                "hi": """समझ गया! 👍

*आपकी अनुमानित मासिक आय कितनी है?*
_(राशि टाइप करें, जैसे 25000 या 25k)_""",
                "ta": """புரிந்தது! 👍

*உங்கள் தோராயமான மாத வருமானம் என்ன?*
_(தொகையை டைப் செய்யுங்கள், உ.ம்., 25000 அல்லது 25k)_""",
                "te": """అర్థమైంది! 👍

*మీ సుమారు నెలవారీ ఆదాయం ఎంత?*
_(మొత్తం టైప్ చేయండి, ఉ.దా., 25000 లేదా 25k)_"""
            }
            return responses.get(lang, responses["en"])
        
        elif step == 4:  # Got income
            amount = self._extract_amount(message)
            lang = user_data.get("language", "en")
            if amount:
                user_data["monthly_income"] = amount
                user_data["onboarding_step"] = 5
                user_repo.update_user(phone, user_data)
                
                responses = {
                    "en": """💰 *Now let's set your financial goal!*

What would you like to achieve?
(e.g., Save for a bike, Build emergency fund, Clear debt)""",
                    "hi": """💰 *अब अपना वित्तीय लक्ष्य निर्धारित करें!*

आप क्या हासिल करना चाहते हैं?
(जैसे: बाइक के लिए बचत, आपातकालीन फंड, कर्ज चुकाना)""",
                    "ta": """💰 *இப்போது உங்கள் நிதி இலக்கை அமைப்போம்!*

நீங்கள் என்ன சாதிக்க விரும்புகிறீர்கள்?
(உ.ம்., பைக் வாங்க சேமிப்பு, அவசரகால நிதி, கடன் தீர்க்க)""",
                    "te": """💰 *ఇప్పుడు మీ ఆర్థిక లక్ష్యాన్ని సెట్ చేద్దాం!*

మీరు ఏమి సాధించాలనుకుంటున్నారు?
(ఉ.దా., బైక్ కోసం సేవ్, అత్యవసర నిధి, అప్పు తీర్చడం)"""
                }
                return responses.get(lang, responses["en"])
            else:
                errors = {
                    "en": "🔢 Please type your monthly income (e.g., 25000 or 25k)",
                    "hi": "🔢 कृपया अपनी मासिक आय टाइप करें (जैसे 25000 या 25k)",
                    "ta": "🔢 உங்கள் மாத வருமானத்தை டைப் செய்யுங்கள் (உ.ம்., 25000 அல்லது 25k)",
                    "te": "🔢 దయచేసి మీ నెలవారీ ఆదాయాన్ని టైప్ చేయండి (ఉ.దా., 25000 లేదా 25k)"
                }
                return errors.get(lang, errors["en"])
        
        elif step == 5:  # Got goal
            user_data["goal_type"] = message.strip().title()
            user_data["onboarding_step"] = 6
            user_repo.update_user(phone, user_data)
            lang = user_data.get("language", "en")
            goal = user_data["goal_type"]
            
            responses = {
                "en": f"""Great goal: *{goal}*! 🎯

*How much do you want to save/achieve?*
(Type amount, e.g., 100000 or 1 lakh)""",
                "hi": f"""बढ़िया लक्ष्य: *{goal}*! 🎯

*आप कितना बचाना/हासिल करना चाहते हैं?*
(राशि टाइप करें, जैसे 100000 या 1 लाख)""",
                "ta": f"""அருமையான இலக்கு: *{goal}*! 🎯

*நீங்கள் எவ்வளவு சேமிக்க/சாதிக்க விரும்புகிறீர்கள்?*
(தொகையை டைப் செய்யுங்கள், உ.ம்., 100000 அல்லது 1 லட்சம்)""",
                "te": f"""గొప్ప లక్ష్యం: *{goal}*! 🎯

*మీరు ఎంత సేవ్ చేయాలనుకుంటున్నారు/సాధించాలనుకుంటున్నారు?*
(మొత్తం టైప్ చేయండి, ఉ.దా., 100000 లేదా 1 లక్ష)"""
            }
            return responses.get(lang, responses["en"])
        
        elif step == 6:  # Got target
            amount = self._extract_amount(message)
            lang = user_data.get("language", "en")
            if amount:
                user_data["target_amount"] = amount
                user_data["onboarding_step"] = 7
                user_repo.update_user(phone, user_data)
                
                responses = {
                    "en": """📅 *And by when do you want to achieve this?*
(e.g., 6 months, 1 year, December 2024)""",
                    "hi": """📅 *और आप इसे कब तक हासिल करना चाहते हैं?*
(जैसे 6 महीने, 1 साल, दिसंबर 2024)""",
                    "ta": """📅 *இதை எப்போது சாதிக்க விரும்புகிறீர்கள்?*
(உ.ம்., 6 மாதங்கள், 1 வருடம், டிசம்பர் 2024)""",
                    "te": """📅 *దీన్ని ఎప్పటికి సాధించాలనుకుంటున్నారు?*
(ఉ.దా., 6 నెలలు, 1 సంవత్సరం, డిసెంబర్ 2024)"""
                }
                return responses.get(lang, responses["en"])
            else:
                errors = {
                    "en": "🔢 Please type the target amount (e.g., 100000 or 1 lakh)",
                    "hi": "🔢 कृपया लक्ष्य राशि टाइप करें (जैसे 100000 या 1 लाख)",
                    "ta": "🔢 இலக்கு தொகையை டைப் செய்யுங்கள் (உ.ம்., 100000 அல்லது 1 லட்சம்)",
                    "te": "🔢 దయచేసి లక్ష్య మొత్తాన్ని టైప్ చేయండి (ఉ.దా., 100000 లేదా 1 లక్ష)"
                }
                return errors.get(lang, errors["en"])
        
        elif step == 7:  # Got timeline
            months = self._parse_timeline(message)
            days = months * 30
            lang = user_data.get("language", "en")
            
            # Timeline string based on language
            if lang == "ta":
                timeline_str = f"{months} மாதங்கள்" if months < 24 else f"{months/12:.1f} வருடங்கள்"
            elif lang == "hi":
                timeline_str = f"{months} महीने" if months < 24 else f"{months/12:.1f} साल"
            elif lang == "te":
                timeline_str = f"{months} నెలలు" if months < 24 else f"{months/12:.1f} సంవత్సరాలు"
            else:
                timeline_str = f"{months} Months" if months < 24 else f"{months/12:.1f} Years"
            
            user_data["timeline"] = timeline_str
            user_data["timeline_days"] = days
            user_data["onboarding_complete"] = True
            user_data["onboarding_step"] = 8
            user_data["start_date"] = datetime.now().isoformat()
            
            # Calculate targets
            target = user_data.get("target_amount", 100000)
            monthly_income = user_data.get("monthly_income", 30000)
            daily_target = round(target / max(1, days))
            monthly_target = round(target / max(1, months))
            
            # Daily budget = (monthly income / 30) - daily savings target
            # But ensure minimum budget of ₹200
            daily_budget = max(500, (monthly_income // 30) - daily_target)
            
            user_data["daily_target"] = daily_target
            user_data["daily_budget"] = daily_budget
            user_data["monthly_target"] = monthly_target
            
            user_repo.update_user(phone, user_data)
            
            name = user_data.get('name', 'Friend')
            work = user_data.get('occupation', 'User')
            goal = user_data.get('goal_type', 'Savings')
            
            responses = {
                "en": f"""🎉 *Your profile is ready!*

📊 *Your Financial Plan:*
━━━━━━━━━━━━━━━━━
👤 Name: {name}
💼 Work: {work}
💰 Income: ₹{monthly_income:,}/month
🎯 Goal: {goal}
💵 Target: ₹{target:,}
📅 Timeline: {timeline_str}
━━━━━━━━━━━━━━━━━

📈 *Daily Target:* ₹{daily_target:,}
📅 *Monthly Target:* ₹{monthly_target:,}
💸 *Daily Budget:* ₹{daily_budget:,}

I'll send you:
⏰ Morning reminder at 6 AM
📊 Daily summary at 8 PM
📈 Weekly progress report

*Type "help" anytime for assistance!*
*Start tracking: "Spent 50 on tea"*""",

                "ta": f"""🎉 *உங்கள் சுயவிவரம் தயார்!*

📊 *உங்கள் நிதி திட்டம்:*
━━━━━━━━━━━━━━━━━
👤 பெயர்: {name}
💼 வேலை: {work}
💰 வருமானம்: ₹{monthly_income:,}/மாதம்
🎯 இலக்கு: {goal}
💵 இலக்கு தொகை: ₹{target:,}
📅 காலம்: {timeline_str}
━━━━━━━━━━━━━━━━━

📈 *தினசரி இலக்கு:* ₹{daily_target:,}
📅 *மாதாந்திர இலக்கு:* ₹{monthly_target:,}
💸 *தினசரி பட்ஜெட்:* ₹{daily_budget:,}

நான் அனுப்புவேன்:
⏰ காலை நினைவூட்டல் 6 AM
📊 தினசரி சுருக்கம் 8 PM
📈 வாராந்திர முன்னேற்ற அறிக்கை

*எப்போது வேண்டுமானாலும் "help" என டைப் செய்யுங்கள்!*
*தொடங்குங்கள்: "டீக்கு 50 செலவழித்தேன்"*""",

                "hi": f"""🎉 *आपकी प्रोफ़ाइल तैयार है!*

📊 *आपकी वित्तीय योजना:*
━━━━━━━━━━━━━━━━━
👤 नाम: {name}
💼 काम: {work}
💰 आय: ₹{monthly_income:,}/महीना
🎯 लक्ष्य: {goal}
💵 लक्ष्य राशि: ₹{target:,}
📅 समय: {timeline_str}
━━━━━━━━━━━━━━━━━

📈 *दैनिक लक्ष्य:* ₹{daily_target:,}
📅 *मासिक लक्ष्य:* ₹{monthly_target:,}
💸 *दैनिक बजट:* ₹{daily_budget:,}

मैं भेजूंगा:
⏰ सुबह 6 बजे याद दिलाना
📊 रात 8 बजे दैनिक सारांश
📈 साप्ताहिक प्रगति रिपोर्ट

*कभी भी मदद के लिए "help" टाइप करें!*
*शुरू करें: "चाय पर 50 खर्च किए"*""",

                "te": f"""🎉 *మీ ప్రొఫైల్ సిద్ధంగా ఉంది!*

📊 *మీ ఆర్థిక ప్రణాళిక:*
━━━━━━━━━━━━━━━━━
👤 పేరు: {name}
💼 పని: {work}
💰 ఆదాయం: ₹{monthly_income:,}/నెల
🎯 లక్ష్యం: {goal}
💵 లక్ష్య మొత్తం: ₹{target:,}
📅 సమయం: {timeline_str}
━━━━━━━━━━━━━━━━━

📈 *రోజువారీ లక్ష్యం:* ₹{daily_target:,}
📅 *నెలవారీ లక్ష్యం:* ₹{monthly_target:,}
💸 *రోజువారీ బడ్జెట్:* ₹{daily_budget:,}

నేను పంపుతాను:
⏰ ఉదయం 6 గంటలకు రిమైండర్
📊 రాత్రి 8 గంటలకు సారాంశం
📈 వారపు ప్రగతి నివేదిక

*సహాయం కోసం ఎప్పుడైనా "help" టైప్ చేయండి!*
*ప్రారంభించండి: "టీకి 50 ఖర్చు"*"""
            }
            
            return responses.get(lang, responses["en"])
        
        return self._handle_help(message, user_data, {}, context)
    
    def _parse_timeline(self, text: str) -> int:
        """Parse timeline from text, returns months"""
        text = text.lower()
        months = 12  # default
        
        if "month" in text:
            nums = re.findall(r'\d+', text)
            if nums:
                months = int(nums[0])
        elif "year" in text:
            nums = re.findall(r'\d+', text)
            if nums:
                months = int(nums[0]) * 12
        elif text.strip().isdigit():
            num = int(text.strip())
            if num <= 5:
                months = num * 12
            else:
                months = num
        
        return months
    
    # =================== REMINDER GENERATORS ===================
    
    def generate_morning_reminder(self, user_data: Dict) -> str:
        """Generate personalized morning reminder"""
        name = user_data.get("name", "Friend")
        daily_budget = user_data.get("daily_budget", 500)
        daily_target = user_data.get("daily_target", 200)
        
        # Get yesterday's data
        phone = user_data.get("phone")
        yesterday_saved = self._get_yesterday_savings(phone)
        
        motivations = [
            "💪 \"Small daily savings lead to big dreams!\"",
            "🌟 \"Every rupee saved is a step towards your goal!\"",
            "🔥 \"Consistency beats intensity. Keep going!\"",
            "✨ \"Today is a new opportunity to save!\"",
        ]
        
        tips = [
            "Pack lunch to save ₹100 today!",
            "Compare prices before buying anything.",
            "Avoid impulse purchases - wait 24 hours.",
            "Use public transport when possible.",
        ]
        
        lang = user_data.get("language", "en")
        template = self.templates.get(lang, self.templates["en"])["morning_reminder"]
        
        return template.format(
            name=name,
            daily_budget=daily_budget,
            daily_target=daily_target,
            yesterday_saved=yesterday_saved,
            motivation=random.choice(motivations),
            daily_tip=random.choice(tips)
        )
    
    def generate_evening_checkout(self, user_data: Dict) -> str:
        """Generate evening checkout message"""
        phone = user_data.get("phone")
        name = user_data.get("name", "Friend")
        
        # Get today's data
        today_income = self._get_today_income(phone)
        today_expenses = self._get_today_expenses(phone)
        net = today_income - today_expenses
        
        # Get goal info
        goal = self._get_active_goal(phone)
        target = goal.get("target_amount", 100000) if goal else 100000
        progress = self._get_goal_progress(phone)
        saved = int(target * progress / 100)
        
        # Comparison
        if net > 0:
            comparison = f"✅ Great! You saved ₹{net} today!"
        elif net == 0:
            comparison = "➖ Break-even day. Try to save tomorrow!"
        else:
            comparison = f"⚠️ You overspent by ₹{abs(net)}. Let's plan better tomorrow."
        
        # Progress bar
        filled = int(progress / 10)
        progress_bar = "█" * filled + "░" * (10 - filled)
        
        # Advice
        advices = [
            "💡 Review your spending categories weekly!",
            "💡 Set aside savings first thing in the morning!",
            "💡 Every small expense adds up - track them all!",
        ]
        
        lang = user_data.get("language", "en")
        template = self.templates.get(lang, self.templates["en"])["evening_checkout"]
        
        return template.format(
            date=datetime.now().strftime("%d %b %Y"),
            income=today_income,
            expenses=today_expenses,
            net=net,
            comparison=comparison,
            progress_bar=progress_bar,
            saved=saved,
            target=target,
            progress=progress,
            advice=random.choice(advices)
        )
    
    # =================== DATA HELPERS ===================
    
    def _get_today_expenses(self, phone: str) -> int:
        """Get today's total expenses"""
        try:
            transactions = transaction_repo.get_transactions(phone)
            today = datetime.now().date()
            total = 0
            for tx in transactions:
                if tx.get("type") == "expense":
                    tx_date = datetime.fromisoformat(tx.get("date", "")).date()
                    if tx_date == today:
                        total += tx.get("amount", 0)
            return total
        except:
            return 0
    
    def _get_today_income(self, phone: str) -> int:
        """Get today's total income"""
        try:
            transactions = transaction_repo.get_transactions(phone)
            today = datetime.now().date()
            total = 0
            for tx in transactions:
                if tx.get("type") == "income":
                    tx_date = datetime.fromisoformat(tx.get("date", "")).date()
                    if tx_date == today:
                        total += tx.get("amount", 0)
            return total
        except:
            return 0
    
    def _get_month_expenses(self, phone: str) -> int:
        """Get this month's total expenses"""
        try:
            transactions = transaction_repo.get_transactions(phone)
            now = datetime.now()
            total = 0
            for tx in transactions:
                if tx.get("type") == "expense":
                    tx_date = datetime.fromisoformat(tx.get("date", ""))
                    if tx_date.year == now.year and tx_date.month == now.month:
                        total += tx.get("amount", 0)
            return total
        except:
            return 0
    
    def _get_month_income(self, phone: str) -> int:
        """Get this month's total income"""
        try:
            transactions = transaction_repo.get_transactions(phone)
            now = datetime.now()
            total = 0
            for tx in transactions:
                if tx.get("type") == "income":
                    tx_date = datetime.fromisoformat(tx.get("date", ""))
                    if tx_date.year == now.year and tx_date.month == now.month:
                        total += tx.get("amount", 0)
            return total
        except:
            return 0
    
    def _get_yesterday_savings(self, phone: str) -> int:
        """Get yesterday's net savings"""
        try:
            transactions = transaction_repo.get_transactions(phone)
            yesterday = (datetime.now() - timedelta(days=1)).date()
            income = 0
            expense = 0
            for tx in transactions:
                tx_date = datetime.fromisoformat(tx.get("date", "")).date()
                if tx_date == yesterday:
                    if tx.get("type") == "income":
                        income += tx.get("amount", 0)
                    else:
                        expense += tx.get("amount", 0)
            return income - expense
        except:
            return 0
    
    def _get_goal_progress(self, phone: str) -> int:
        """Get goal progress percentage"""
        try:
            user = user_repo.get_user(phone)
            if not user:
                return 0
            
            target = user.get("target_amount", 100000)
            # Calculate total savings since start
            start_date = user.get("start_date")
            if not start_date:
                return 0
            
            transactions = transaction_repo.get_transactions(phone)
            start = datetime.fromisoformat(start_date)
            
            total_saved = 0
            for tx in transactions:
                tx_date = datetime.fromisoformat(tx.get("date", ""))
                if tx_date >= start:
                    if tx.get("type") == "income":
                        total_saved += tx.get("amount", 0)
                    else:
                        total_saved -= tx.get("amount", 0)
            
            progress = int((max(0, total_saved) / target) * 100)
            return min(100, progress)
        except:
            return 0
    
    def _get_active_goal(self, phone: str) -> Optional[Dict]:
        """Get user's active goal"""
        try:
            user = user_repo.get_user(phone)
            if not user:
                return None
            
            if not user.get("target_amount"):
                return None
            
            start_date = user.get("start_date")
            if start_date:
                start = datetime.fromisoformat(start_date)
                days_elapsed = (datetime.now() - start).days
                timeline_days = user.get("timeline_days", 365)
                days_left = max(0, timeline_days - days_elapsed)
            else:
                days_left = 365
            
            return {
                "name": user.get("goal_type", "Savings Goal"),
                "target_amount": user.get("target_amount", 100000),
                "days_left": days_left,
                "timeline": user.get("timeline", "1 Year"),
            }
        except:
            return None
    
    def _get_today_income(self, phone: str) -> int:
        """Get today's total income accumulated"""
        try:
            import pytz
            ist = pytz.timezone('Asia/Kolkata')
            today = datetime.now(ist).date()
            
            transactions = transaction_repo.get_transactions(phone)
            total = 0
            print(f"[AccumulatedIncome] Checking {len(transactions) if transactions else 0} transactions for {phone}")
            
            for tx in transactions:
                if tx.get("type") == "income":
                    tx_date_str = tx.get("date", "")
                    try:
                        # Handle timezone-aware dates
                        if "+" in tx_date_str:
                            tx_date_str = tx_date_str.split("+")[0]  # Remove timezone
                        tx_date = datetime.fromisoformat(tx_date_str).date()
                        
                        if tx_date == today:
                            amt = tx.get("amount", 0)
                            total += amt
                            print(f"[AccumulatedIncome] Found ₹{amt} ({tx_date})")
                    except Exception as parse_err:
                        print(f"[AccumulatedIncome] Parse error: {parse_err}")
            
            print(f"[AccumulatedIncome] Total for today: ₹{total}")
            return total
        except Exception as e:
            print(f"Error getting today income: {e}")
            return 0
    
    def _get_today_expenses(self, phone: str) -> int:
        """Get today's total expenses accumulated"""
        try:
            import pytz
            ist = pytz.timezone('Asia/Kolkata')
            today = datetime.now(ist).date()
            
            transactions = transaction_repo.get_transactions(phone)
            total = 0
            for tx in transactions:
                if tx.get("type") == "expense":
                    tx_date_str = tx.get("date", "")
                    try:
                        if "+" in tx_date_str:
                            tx_date_str = tx_date_str.split("+")[0]
                        tx_date = datetime.fromisoformat(tx_date_str).date()
                        if tx_date == today:
                            total += tx.get("amount", 0)
                    except:
                        pass
            return total
        except Exception as e:
            print(f"Error getting today expenses: {e}")
            return 0
    
    def _get_month_income(self, phone: str) -> int:
        """Get this month's total income"""
        try:
            import pytz
            ist = pytz.timezone('Asia/Kolkata')
            now = datetime.now(ist)
            
            transactions = transaction_repo.get_transactions(phone)
            total = 0
            for tx in transactions:
                if tx.get("type") == "income":
                    tx_date = datetime.fromisoformat(tx.get("date", ""))
                    if tx_date.year == now.year and tx_date.month == now.month:
                        total += tx.get("amount", 0)
            return total
        except:
            return 0
    
    def _get_month_expenses(self, phone: str) -> int:
        """Get this month's total expenses"""
        try:
            import pytz
            ist = pytz.timezone('Asia/Kolkata')
            now = datetime.now(ist)
            
            transactions = transaction_repo.get_transactions(phone)
            total = 0
            for tx in transactions:
                if tx.get("type") == "expense":
                    tx_date = datetime.fromisoformat(tx.get("date", ""))
                    if tx_date.year == now.year and tx_date.month == now.month:
                        total += tx.get("amount", 0)
            return total
        except:
            return 0
    
    def _get_category_breakdown(self, phone: str) -> Dict[str, int]:
        """Get expense breakdown by category"""
        try:
            transactions = transaction_repo.get_transactions(phone)
            now = datetime.now()
            categories = {}
            
            for tx in transactions:
                if tx.get("type") == "expense":
                    tx_date = datetime.fromisoformat(tx.get("date", ""))
                    if tx_date.year == now.year and tx_date.month == now.month:
                        cat = tx.get("category", "other")
                        categories[cat] = categories.get(cat, 0) + tx.get("amount", 0)
            
            return categories
        except:
            return {"other": 0}


# Create global instance
advanced_agent = AdvancedWhatsAppAgent()
