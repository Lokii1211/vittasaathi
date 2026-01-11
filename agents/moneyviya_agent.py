"""
MoneyViya AI Agent - Core Intelligence
Handles all AI-powered financial advisory conversations

Scenarios:
1. Lokesh (Student) - Save ₹20L in 2 years, needs daily reminders
2. Rajesh (Gig Worker) - Irregular income, needs budgeting
3. Kaviya (Housewife) - Low income, needs savings + extra income ideas
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import requests

class MoneyViyaAgent:
    """AI Financial Agent that works primarily via WhatsApp"""
    
    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY", "")
        self.alpha_vantage_key = os.getenv("ALPHAVANTAGE_API_KEY", "")
        
        # User personas
        self.personas = {
            "student": {
                "name": "Student/Young Professional",
                "focus": ["savings goals", "investment basics", "budgeting"],
                "challenges": ["irregular pocket money", "peer pressure spending"]
            },
            "gig_worker": {
                "name": "Gig Worker/Daily Earner", 
                "focus": ["income tracking", "emergency fund", "irregular income management"],
                "challenges": ["variable income", "no fixed salary", "no benefits"]
            },
            "housewife": {
                "name": "Homemaker",
                "focus": ["household budget", "savings", "extra income ideas"],
                "challenges": ["limited income", "family expenses", "no personal savings"]
            },
            "small_business": {
                "name": "Small Business Owner",
                "focus": ["business finances", "tax planning", "growth investment"],
                "challenges": ["cash flow", "business vs personal", "expansion capital"]
            }
        }
        
        # Conversation templates
        self.templates = {
            "onboarding": {
                "welcome": """🙏 *Welcome to MoneyViya!*

I'm your personal AI Financial Advisor. I'll help you:
✅ Track your income & expenses
✅ Set and achieve savings goals
✅ Get daily reminders & motivation
✅ Learn smart investment tips

*Let's start! What's your name?*""",
                
                "ask_occupation": """Nice to meet you, {name}! 😊

What do you do for work?
(e.g., Student, Delivery Partner, Housewife, Business Owner, or just tell me!)""",
                
                "ask_income": """Got it! 👍

What's your {income_type} income approximately?
(Just type the amount, e.g., 25000)""",
                
                "ask_goal": """💰 Now let's set your financial goal!

What is your main target right now?
(e.g., Buy a Bike, Save 1 Lakh, Clear Loan, Emergency Fund)""",
                
                "ask_target": """Excellent choice! 🎯

How much do you want to save/achieve?
(Type amount, e.g., 100000 for ₹1 Lakh)""",
                
                "ask_timeline": """And by when do you want to achieve this?
(e.g., 6 months, 1 year, Dec 2024)""",
                
                "complete": """🎉 *Your profile is ready!*

📊 *Your Financial Plan:*
━━━━━━━━━━━━━━━━━
👤 Name: {name}
💼 Profile: {occupation}
💰 Income: ₹{income}/month
🎯 Goal: {goal}
💵 Target: ₹{target}
📅 Timeline: {timeline}
━━━━━━━━━━━━━━━━━

📈 *Daily Target:* ₹{daily_target}
📅 *Monthly Target:* ₹{monthly_target}

I'll send you:
⏰ Morning reminder at 6 AM
📊 Daily summary at 9 PM
📈 Weekly progress report

*Type "help" anytime for assistance!*"""
            },
            
            "daily_reminder": {
                "morning": """☀️ *Good Morning, {name}!*

📅 *Today's Financial Goals:*
━━━━━━━━━━━━━━━━━
💰 Save: ₹{daily_target}
📊 Yesterday: ₹{yesterday_saved} saved
🎯 Goal Progress: {progress}%
━━━━━━━━━━━━━━━━━

{motivation_quote}

💡 *Tip:* {daily_tip}

*Track expense:* Just type "spent 50 on tea"
*Log income:* Type "earned 500 delivery" """,
                
                "evening": """🌙 *Good Evening, {name}!*

📊 *Today's Summary:*
━━━━━━━━━━━━━━━━━
💵 Income: ₹{today_income}
💸 Expenses: ₹{today_expenses}
💰 Saved: ₹{today_saved}
━━━━━━━━━━━━━━━━━

{comparison}

🎯 *Goal Status:*
{goal_progress_bar}
₹{total_saved}/₹{target} ({progress}%)

{personalized_advice}

*Great job! Keep going!* 💪"""
            },
            
            "weekly_report": """📊 *Weekly Financial Report*
{name} | Week {week_number}
━━━━━━━━━━━━━━━━━━━━

💵 *Total Income:* ₹{weekly_income}
💸 *Total Expenses:* ₹{weekly_expenses}
💰 *Net Saved:* ₹{weekly_saved}

📈 *vs Last Week:*
{weekly_comparison}

*Category Breakdown:*
🍽️ Food: ₹{food} ({food_pct}%)
🚗 Transport: ₹{transport} ({transport_pct}%)
📱 Bills: ₹{bills} ({bills_pct}%)
🛍️ Shopping: ₹{shopping} ({shopping_pct}%)
📦 Other: ₹{other} ({other_pct}%)

💡 *AI Insights:*
{ai_insights}

🎯 *Goal Progress:* {progress}%
📅 Days to Goal: {days_left}

*Keep pushing! You're doing great!* 🚀""",

            "investment_tip": """📈 *Investment Idea for You*

Based on your profile ({occupation}):

💰 *Recommended:*
{investment_recommendation}

📊 *Market Update:*
{market_update}

⚠️ *Risk Level:* {risk_level}
💡 *Why this?* {reason}

*Start small, learn big!* 📚""",

            "extra_income_ideas": """💡 *Extra Income Ideas for You*

Based on your profile:

{ideas}

🎯 *Top Recommendation:*
{top_recommendation}

💰 *Potential Earning:* ₹{potential_earning}/month
⏰ *Time Required:* {time_required}

*Want details on any option? Reply with the number!*"""
        }
    
    def process_message(self, phone: str, message: str, user_data: Dict) -> str:
        """Main message processing - the brain of the agent"""
        message = message.strip().lower()
        
        # Check onboarding status
        if not user_data.get("onboarding_complete"):
            return self._handle_onboarding(phone, message, user_data)
        
        # Handle commands
        if message in ["help", "menu", "?", "start"]:
            return self._get_help_menu(user_data)
        
        if message in ["report", "summary", "status"]:
            return self._get_status_report(user_data)
        
        if message in ["goal", "goals", "target"]:
            return self._get_goal_progress(user_data)
        
        if message in ["invest", "investment", "stocks"]:
            return self._get_investment_ideas(user_data)
        
        if message in ["ideas", "extra income", "earn more"]:
            return self._get_extra_income_ideas(user_data)
        
        if message in ["budget", "daily budget"]:
            return self._get_daily_budget(user_data)
        
        # Check for expense logging
        if any(word in message for word in ["spent", "paid", "खर्च", "செலவு"]):
            return self._log_expense(message, user_data)
        
        # Check for income logging
        if any(word in message for word in ["earned", "received", "got", "income", "कमाया", "வருமானம்"]):
            return self._log_income(message, user_data)
        
        # Simple confirmations
        if message in ["yes", "yeah", "yep", "correct", "complete", "done", "confirm"]:
            return "✅ *Great!* I've updated your records. Day closed! 🌙"
            
        if message in ["no", "nope", "wait", "add more"]:
            return "Okay! Just type what else you want to add (e.g. 'Spent 50 on milk')."

        # OTP Request (Fallback for Baileys/Free users)
        if any(w in message for w in ["otp", "login code", "verification code"]):
            import random
            import time
            otp = str(random.randint(100000, 999999))
            user_data["temp_otp"] = otp
            user_data["otp_expiry"] = time.time() + 300
            return f"🔐 Your MoneyViya Login OTP is: *{otp}*\n\n(Valid for 5 minutes). Enter this on the website to log in."

        # Investment Advice
        if any(w in message for w in ["invest", "market", "stock", "mutual fund", "gold", "sip", "trend", "advice", "plan"]):
            return self._recommend_investment(message, user_data)

        # Use AI for natural conversation
        return self._ai_conversation(message, user_data)
    
    def _handle_onboarding(self, phone: str, message: str, user_data: Dict) -> str:
        """Handle user onboarding flow"""
        step = user_data.get("onboarding_step", 0)
        
        # Normalize step if it comes from old system (strings like "language", "name")
        if isinstance(step, str):
            step = 0
            user_data["onboarding_step"] = 0
        
        if step == 0:
            user_data["onboarding_step"] = 1
            return self.templates["onboarding"]["welcome"]
        
        elif step == 1:  # Got name
            user_data["name"] = message.strip().title()
            user_data["onboarding_step"] = 2
            return self.templates["onboarding"]["ask_occupation"].format(name=user_data["name"])
        
        elif step == 2:  # Got occupation
            user_data["occupation"] = message.strip().title()
            
            # Heuristics for internal logic
            msg = message.lower()
            occ_type = "general"
            if "student" in msg: occ_type = "student"
            elif any(w in msg for w in ["gig", "delivery", "driver", "uber", "zomato"]): occ_type = "gig_worker"
            elif any(w in msg for w in ["house", "home", "mom"]): occ_type = "housewife"
            
            user_data["occupation_type"] = occ_type
            user_data["onboarding_step"] = 3
            
            return self.templates["onboarding"]["ask_income"].format(income_type="monthly")
        
        elif step == 3:  # Got income
            import re
            try:
                # Extract first number found
                numbers = re.findall(r'\d+', message.replace(",", ""))
                if numbers:
                    income = int(numbers[0])
                    # Handle basic units like "20k"
                    if "k" in message.lower():
                        income *= 1000
                    if "l" in message.lower() or "lakh" in message.lower():
                        income *= 100000
                    user_data["monthly_income"] = income
                else:
                    return "🔢 Please type just the amount (e.g. 25000)"
            except:
                return "🔢 Please type a valid number for income."
                
            user_data["onboarding_step"] = 4
            return self.templates["onboarding"]["ask_goal"]
        
        elif step == 4:  # Got goal type
            # Free text goal
            user_data["goal_type"] = message.strip().title()
            user_data["onboarding_step"] = 5
            return self.templates["onboarding"]["ask_target"]
        
        elif step == 5:  # Got target amount
            import re
            try:
                numbers = re.findall(r'\d+', message.replace(",", ""))
                if numbers:
                    target = int(numbers[0])
                    if "k" in message.lower(): target *= 1000
                    if "l" in message.lower() or "lakh" in message.lower(): target *= 100000
                    user_data["target_amount"] = target
                else:
                    return "🔢 Please type just the amount (e.g. 100000)"
            except:
                return "🔢 Please type a valid target amount."
            
            user_data["onboarding_step"] = 6
            return self.templates["onboarding"]["ask_timeline"]
        
        elif step == 6:  # Got timeline
            msg = message.lower()
            import re
            months = 12
            
            # Parse text (e.g., "6 months", "2 years")
            if "month" in msg:
                 nums = re.findall(r'\d+', msg)
                 if nums: months = int(nums[0])
            elif "year" in msg:
                 nums = re.findall(r'\d+', msg)
                 if nums: months = int(nums[0]) * 12
            elif msg.strip().isdigit():
                 num = int(msg.strip())
                 # Heuristic: < 5 likely years, > 5 likely months
                 if num <= 5: months = num * 12 
                 else: months = num 
            
            days = months * 30
            timeline_str = f"{months} Months" if months < 24 else f"{months/12:.1f} Years"
            
            user_data["timeline"] = timeline_str
            user_data["timeline_days"] = days
            user_data["onboarding_complete"] = True
            user_data["onboarding_step"] = 7
            user_data["start_date"] = datetime.now().isoformat()
            
            # Calculate targets
            target = user_data.get("target_amount", 100000)
            daily_target = round(target / max(1, days))
            monthly_target = round(target / max(0.1, (days / 30)))
            
            user_data["daily_target"] = daily_target
            
            return self.templates["onboarding"]["complete"].format(
                name=user_data.get("name", "Friend"),
                occupation=user_data.get("occupation", "User"),
                income=user_data.get("monthly_income", 0),
                goal=user_data.get("goal_type", "Savings"),
                target=target,
                timeline=timeline_str,
                daily_target=daily_target,
                monthly_target=monthly_target
            )
        
        return self.templates["onboarding"]["welcome"]
    
    def _log_expense(self, message: str, user_data: Dict) -> str:
        """Log expense from natural language"""
        import re
        
        # Extract amount
        numbers = re.findall(r'\d+', message)
        amount = int(numbers[0]) if numbers else 0
        
        # Detect category
        category = "other"
        if any(w in message for w in ["food", "tea", "chai", "lunch", "dinner", "eat", "சாப்பாடு"]):
            category = "food"
        elif any(w in message for w in ["auto", "bus", "petrol", "uber", "ola", "travel", "பயணம்"]):
            category = "transport"
        elif any(w in message for w in ["bill", "recharge", "electricity", "rent", "வாடகை"]):
            category = "bills"
        elif any(w in message for w in ["shop", "amazon", "flipkart", "clothes", "ஷாப்பிங்"]):
            category = "shopping"
        
        if amount > 0:
            # Save to database (would be actual DB call)
            return f"""✅ *Expense Recorded!*

💸 Amount: ₹{amount}
📁 Category: {category.title()}
📅 Date: {datetime.now().strftime('%d %b, %I:%M %p')}

💰 *Today's Total:* ₹{amount}
🎯 *Daily Budget Left:* ₹{max(0, user_data.get('daily_budget', 500) - amount)}

_Keep tracking! Every rupee counts!_ 💪"""
        
        return "❓ Couldn't understand the amount. Try: 'spent 50 on tea'"
    
    def _log_income(self, message: str, user_data: Dict) -> str:
        """Log income from natural language"""
        import re
        
        numbers = re.findall(r'\d+', message)
        amount = int(numbers[0]) if numbers else 0
        
        # Detect source
        source = "other"
        if any(w in message for w in ["delivery", "swiggy", "zomato", "uber"]):
            source = "gig"
        elif any(w in message for w in ["salary", "wages"]):
            source = "salary"
        elif any(w in message for w in ["freelance", "project"]):
            source = "freelance"
        
        if amount > 0:
            return f"""✅ *Income Recorded!*

💵 Amount: ₹{amount}
📁 Source: {source.title()}
📅 Date: {datetime.now().strftime('%d %b, %I:%M %p')}

💰 *Today's Earnings:* ₹{amount}
🎯 *Goal Progress:* +₹{amount} closer!

_Great work! Keep earning!_ 🚀"""
        
        return "❓ Couldn't understand. Try: 'earned 500 from delivery'"
    
    def _get_help_menu(self, user_data: Dict) -> str:
        """Get help menu"""
        name = user_data.get("name", "Friend")
        return f"""📚 *MoneyViya Help*

Hi {name}! Here's what I can do:

💸 *Track Expenses:*
"spent 50 on tea"
"paid 200 for auto"

💵 *Log Income:*
"earned 500 delivery"
"got 1000 freelance"

📊 *Reports:*
"report" - Today's summary
"weekly" - Week report
"monthly" - Month report

🎯 *Goals:*
"goal" - Check progress
"budget" - Daily budget

💡 *Ideas:*
"invest" - Investment tips
"ideas" - Extra income ideas

⚙️ *Settings:*
"change goal" - Update goal
"language" - Change language

*Just type naturally, I understand!* 🤖"""
    
    def _get_investment_ideas(self, user_data: Dict) -> str:
        """Get investment ideas using Alpha Vantage"""
        occupation = user_data.get("occupation", "gig_worker")
        income = user_data.get("monthly_income", 20000)
        
        # Personalized recommendations based on profile
        if income < 15000:
            return """📈 *Investment Ideas for You*

💡 *Best for Your Income Level:*

1️⃣ *Post Office RD* 
   - Min: ₹100/month
   - Safe & guaranteed returns
   - 6.5% interest

2️⃣ *SIP in Index Fund*
   - Start: ₹500/month
   - Long term growth
   - Nifty 50 or Sensex

3️⃣ *Digital Gold*
   - Min: ₹10
   - Easy to start
   - Good for beginners

⚠️ *Start Small Tip:*
Even ₹100/month becomes ₹1.3 Lakh in 10 years!

*Reply "details 1" for more info*"""
        
        else:
            return """📈 *Investment Ideas for You*

💡 *Recommended Portfolio:*

1️⃣ *Emergency Fund (3 months)* - First priority
   - Keep in savings account or liquid fund
   
2️⃣ *SIP in Mutual Funds* - ₹2000/month
   - Mix of equity & debt funds
   
3️⃣ *PPF Account* - ₹500/month
   - Tax saving + guaranteed returns
   
4️⃣ *Stock Market* - After 6 months learning
   - Start with index ETFs

📊 *Market Update:*
NIFTY 50: Good for long term
Gold: Stable, good hedge

*Reply "sip" or "ppf" for details*"""
    
    def _get_extra_income_ideas(self, user_data: Dict) -> str:
        """Get extra income ideas based on profile"""
        occupation = user_data.get("occupation", "gig_worker")
        
        if occupation == "housewife":
            return """💡 *Extra Income Ideas for Homemakers*

🏠 *Work from Home Options:*

1️⃣ *Tiffin Service*
   💰 ₹10,000-30,000/month
   ⏰ 4-5 hours/day
   
2️⃣ *Online Tutoring*
   💰 ₹5,000-15,000/month
   ⏰ 2-3 hours/day
   
3️⃣ *Handicrafts on Etsy/Amazon*
   💰 ₹3,000-20,000/month
   ⏰ Flexible
   
4️⃣ *Data Entry Jobs*
   💰 ₹8,000-15,000/month
   ⏰ 3-4 hours/day
   
5️⃣ *YouTube/Instagram*
   💰 ₹0-50,000/month
   ⏰ 2 hours/day

🎯 *My Pick for You:* Tiffin Service
Low investment, high demand!

*Reply number for detailed guide*"""
        
        elif occupation == "student":
            return """💡 *Extra Income Ideas for Students*

📚 *Part-time Options:*

1️⃣ *Online Tutoring*
   💰 ₹200-500/hour
   
2️⃣ *Freelancing* (Fiverr/Upwork)
   💰 ₹5,000-50,000/month
   
3️⃣ *Content Writing*
   💰 ₹2-5 per word
   
4️⃣ *Social Media Management*
   💰 ₹5,000-15,000/month
   
5️⃣ *Internships*
   💰 ₹5,000-25,000/month

🎯 *Start with:* Freelancing
Build skills + earn!

*Reply number for guide*"""
        
        else:
            return """💡 *Extra Income Ideas*

⚡ *Quick Earning Options:*

1️⃣ *Multiple Gig Apps*
   - Swiggy + Zomato + Dunzo
   💰 Increase earnings 50%+
   
2️⃣ *Referral Bonuses*
   - Refer friends to apps
   💰 ₹100-500 per referral
   
3️⃣ *Weekend Work*
   - Event helper, moving help
   💰 ₹500-1000/day
   
4️⃣ *Sell Skills*
   - Teach what you know
   💰 ₹200-500/hour

💡 *Pro Tip:* Track peak hours, work smarter!

*Reply number for details*"""
    
    def _ai_conversation(self, message: str, user_data: Dict) -> str:
        """Use OpenAI for natural conversation"""
        if not self.openai_key:
            return self._get_help_menu(user_data)
        
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openai_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {
                            "role": "system",
                            "content": f"""You are MoneyViya, a friendly AI financial advisor for Indian users.
User Profile:
- Name: {user_data.get('name', 'Friend')}
- Occupation: {user_data.get('occupation', 'unknown')}
- Monthly Income: ₹{user_data.get('monthly_income', 'unknown')}
- Goal: {user_data.get('goal_type', 'savings')} of ₹{user_data.get('target_amount', 'unknown')}

Be helpful, encouraging, and give practical Indian financial advice.
Use emojis. Keep responses short (under 200 words).
Focus on actionable tips. Mention specific amounts when possible."""
                        },
                        {"role": "user", "content": message}
                    ],
                    "max_tokens": 300,
                    "temperature": 0.7
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"OpenAI Error: {e}")
        
        return self._get_help_menu(user_data)
    
    def generate_evening_checkout(self, user_data: Dict) -> str:
        """
        8 PM Specific Logic:
        - Check if data entered today
        - If yes: Summarize and ask if complete
        - If no: Ask for totals
        """
        name = user_data.get("name", "Friend")
        today_income = user_data.get("today_income", 0)
        today_expenses = user_data.get("today_expenses", 0)
        today_invested = user_data.get("today_inv", 0)
        
        has_data = today_income > 0 or today_expenses > 0 or today_invested > 0
        
        if has_data:
            return f"""🌙 *Daily Closing: 8 PM Check*

Hi {name}, here is what you tracked today:

💰 *Income:* ₹{today_income}
💸 *Expense:* ₹{today_expenses}
📈 *Invested:* ₹{today_invested}

*Is this complete?*
Reply with:
"Yes" - to close the day
"No" - to add missing details (e.g., "Spent 50 more on milk")"""
        
        else:
            return f"""🌙 *Daily Closing: 8 PM Check*

Hi {name}, we haven't tracked anything today yet! 📉

*Please tell me your totals for today:*
(You can type like this)

"Earned 1000, Confirmed 500 expenses"
OR
"0 income, 200 expense"

_I'll update your dashboard immediately!_"""

    def generate_daily_reminder(self, user_data: Dict, time_of_day: str = "morning") -> str:
        """Generate daily reminder message"""
        if time_of_day == "evening":
            return self.generate_evening_checkout(user_data)
            
        name = user_data.get("name", "Friend")
        target = user_data.get("target_amount", 100000)
        days = user_data.get("timeline_days", 365)
        daily_target = round(target / days)
        
        # Get progress (would be from database)
        total_saved = user_data.get("total_saved", 0)
        progress = round((total_saved / target) * 100, 1) if target > 0 else 0
        
        motivation_quotes = [
            "💪 Small steps lead to big changes!",
            "🌟 Every rupee saved is a rupee earned!",
            "🚀 Your future self will thank you!",
            "💡 Financial freedom starts today!",
            "🎯 Stay focused, stay winning!"
        ]
        
        daily_tips = [
            "Pack lunch from home to save ₹100+ daily",
            "Use UPI cashback offers for extra savings",
            "Track every expense, no matter how small",
            "Set up auto-save for your salary day",
            "Compare prices before buying anything"
        ]
        
        import random
        
        return self.templates["daily_reminder"]["morning"].format(
            name=name,
            daily_target=daily_target,
            yesterday_saved=user_data.get("yesterday_saved", 0),
            progress=progress,
            motivation_quote=random.choice(motivation_quotes),
            daily_tip=random.choice(daily_tips)
        )

    def _recommend_investment(self, message: str, user_data: Dict) -> str:
        try:
            from services.investment_service import investment_service
            import re
            
            # Check for amount
            msg = message.lower()
            amount_match = re.search(r'\b(\d{3,})\b', msg) # At least 3 digits
            
            if amount_match and ("invest" in msg or "plan" in msg):
                amount = float(amount_match.group(1))
                return investment_service.get_portfolio_plan(amount)
            
            # Else default to analysis
            return investment_service.get_market_analysis()

        except Exception as e:
             print(f"Invest Error: {e}")
             return "I'm analyzing the market trends... Ask me 'Investment ideas' again in a moment!"
             
    def _get_personalized_advice(self, user_data: Dict) -> str:
        """Get personalized advice based on spending patterns"""
        occupation = user_data.get("occupation", "gig_worker")
        
        if occupation == "gig_worker":
            return "💡 *Tip:* Peak hours are 12-2pm and 7-10pm. Maximize earnings!"
        elif occupation == "housewife":
            return "💡 *Tip:* Try bulk buying groceries to save 15-20%!"
        elif occupation == "student":
            return "💡 *Tip:* Student discounts on apps can save you 10% on food!"
        else:
            return "💡 *Tip:* Review subscriptions monthly, cancel unused ones!"


# Create global agent instance
moneyviya_agent = MoneyViyaAgent()
