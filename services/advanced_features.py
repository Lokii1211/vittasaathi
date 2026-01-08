"""
Advanced Features Service
========================
Gamification, Achievements, Insights, and Smart Features
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import random
import sys

sys.path.append(str(Path(__file__).parent.parent))

from database.user_repository import user_repo
from database.transaction_repository import transaction_repo
from database.goal_repository import goal_repo


class GamificationService:
    """Gamification, achievements, and engagement features"""
    
    def __init__(self):
        self.achievements = self._load_achievements()
        self.tips = self._load_tips()
    
    def _load_achievements(self) -> Dict:
        """Load achievement definitions"""
        return {
            "first_entry": {
                "id": "first_entry",
                "name": "First Step",
                "name_hi": "पहला कदम",
                "description": "Recorded your first transaction",
                "icon": "🌟",
                "points": 10
            },
            "week_streak": {
                "id": "week_streak",
                "name": "Week Warrior",
                "name_hi": "सप्ताह योद्धा",
                "description": "7 day tracking streak",
                "icon": "🔥",
                "points": 50
            },
            "month_streak": {
                "id": "month_streak",
                "name": "Consistency Champion",
                "name_hi": "निरंतरता चैंपियन",
                "description": "30 day tracking streak",
                "icon": "💪",
                "points": 200
            },
            "savings_starter": {
                "id": "savings_starter",
                "name": "Savings Starter",
                "name_hi": "बचत की शुरुआत",
                "description": "Saved ₹1,000",
                "icon": "💰",
                "points": 25
            },
            "savings_pro": {
                "id": "savings_pro",
                "name": "Savings Pro",
                "name_hi": "बचत प्रो",
                "description": "Saved ₹10,000",
                "icon": "🏆",
                "points": 100
            },
            "budget_master": {
                "id": "budget_master",
                "name": "Budget Master",
                "name_hi": "बजट मास्टर",
                "description": "Stayed within budget for a month",
                "icon": "📊",
                "points": 75
            },
            "goal_achiever": {
                "id": "goal_achiever",
                "name": "Goal Achiever",
                "name_hi": "लक्ष्य प्राप्तकर्ता",
                "description": "Completed your first goal",
                "icon": "🎯",
                "points": 150
            },
            "fraud_fighter": {
                "id": "fraud_fighter",
                "name": "Fraud Fighter",
                "name_hi": "फ्रॉड फाइटर",
                "description": "Reported a suspicious transaction",
                "icon": "🛡️",
                "points": 30
            },
            "early_bird": {
                "id": "early_bird",
                "name": "Early Bird",
                "name_hi": "सुबह का पक्षी",
                "description": "Logged income before 8 AM",
                "icon": "🌅",
                "points": 15
            },
            "night_owl": {
                "id": "night_owl",
                "name": "Night Owl",
                "name_hi": "रात का उल्लू",
                "description": "Logged expenses at night",
                "icon": "🦉",
                "points": 15
            }
        }
    
    def _load_tips(self) -> Dict[str, List[str]]:
        """Load financial tips by language"""
        return {
            "en": [
                "💡 Save before you spend - set aside savings as soon as you earn",
                "💡 Track every expense, even ₹10 tea",
                "💡 Emergency fund = 6 months of expenses",
                "💡 Avoid round-amount UPI requests - often scams",
                "💡 Start SIP with just ₹500/month",
                "💡 Pay yourself first - treat savings like a bill",
                "💡 Review expenses weekly to find leaks",
                "💡 Cash spending is harder to track - try digital",
                "💡 No loan EMI should exceed 30% of income",
                "💡 Insurance before investment",
                "💡 Compound interest is your best friend",
                "💡 Avoid lifestyle inflation when income grows",
            ],
            "hi": [
                "💡 खर्च से पहले बचाएं - कमाते ही बचत अलग करें",
                "💡 हर खर्च लिखें, ₹10 की चाय भी",
                "💡 इमरजेंसी फंड = 6 महीने का खर्च",
                "💡 गोल नंबर UPI रिक्वेस्ट से बचें - अक्सर फ्रॉड होता है",
                "💡 सिर्फ ₹500/महीने से SIP शुरू करें",
                "💡 पहले खुद को भुगतान करें - बचत को बिल समझें",
                "💡 हफ्ते में खर्च देखें - लीकेज खोजें",
                "💡 कैश खर्च ट्रैक करना मुश्किल - डिजिटल इस्तेमाल करें",
                "💡 EMI आय के 30% से ज्यादा न हो",
                "💡 निवेश से पहले बीमा",
                "💡 चक्रवृद्धि ब्याज आपका सबसे अच्छा दोस्त है",
                "💡 आय बढ़ने पर lifestyle न बढ़ाएं",
            ],
            "ta": [
                "💡 செலவிடுவதற்கு முன் சேமியுங்கள்",
                "💡 ₹10 டீ கூட பதிவு செய்யுங்கள்",
                "💡 அவசர நிதி = 6 மாத செலவு",
                "💡 ₹500/மாதத்தில் SIP தொடங்குங்கள்",
            ],
            "te": [
                "💡 ఖర్చు చేయడానికి ముందు సేవ్ చేయండి",
                "💡 ₹10 టీ కూడా రికార్డ్ చేయండి",
                "💡 అత్యవసర నిధి = 6 నెలల ఖర్చు",
                "💡 ₹500/నెలలో SIP ప్రారంభించండి",
            ]
        }
    
    def check_achievements(self, user_id: str) -> List[Dict]:
        """Check and award new achievements"""
        
        user = user_repo.get_user(user_id)
        if not user:
            return []
        
        earned = user.get("achievements", [])
        new_achievements = []
        
        # Check streak achievements
        streak = user.get("streak_days", 0)
        
        if streak >= 7 and "week_streak" not in earned:
            new_achievements.append(self.achievements["week_streak"])
            earned.append("week_streak")
        
        if streak >= 30 and "month_streak" not in earned:
            new_achievements.append(self.achievements["month_streak"])
            earned.append("month_streak")
        
        # Check savings
        savings = user.get("current_savings", 0)
        
        if savings >= 1000 and "savings_starter" not in earned:
            new_achievements.append(self.achievements["savings_starter"])
            earned.append("savings_starter")
        
        if savings >= 10000 and "savings_pro" not in earned:
            new_achievements.append(self.achievements["savings_pro"])
            earned.append("savings_pro")
        
        # Check goals
        goals = goal_repo.get_user_goals(user_id, "completed")
        if len(goals) >= 1 and "goal_achiever" not in earned:
            new_achievements.append(self.achievements["goal_achiever"])
            earned.append("goal_achiever")
        
        # Check first entry
        total_txns = user.get("total_income_recorded", 0) + user.get("total_expense_recorded", 0)
        if total_txns > 0 and "first_entry" not in earned:
            new_achievements.append(self.achievements["first_entry"])
            earned.append("first_entry")
        
        # Save updated achievements
        if new_achievements:
            total_points = user.get("points", 0) + sum(a["points"] for a in new_achievements)
            user_repo.update_user(user_id, {
                "achievements": earned,
                "points": total_points
            })
        
        return new_achievements
    
    def get_achievement_message(self, achievement: Dict, language: str = "en") -> str:
        """Build achievement unlock message"""
        
        name = achievement.get(f"name_{language[:2]}", achievement["name"])
        icon = achievement["icon"]
        points = achievement["points"]
        
        if language == "hi":
            return f"\n\n🎉 *बैज अनलॉक!*\n{icon} {name}\n+{points} पॉइंट्स!"
        else:
            return f"\n\n🎉 *Achievement Unlocked!*\n{icon} {name}\n+{points} points!"
    
    def get_user_level(self, user_id: str) -> Dict:
        """Get user's gamification level"""
        
        user = user_repo.get_user(user_id)
        points = user.get("points", 0) if user else 0
        
        levels = [
            (0, "Beginner", "🌱", "शुरुआती"),
            (50, "Learner", "📚", "सीखने वाला"),
            (100, "Saver", "💰", "बचतकर्ता"),
            (200, "Tracker", "📊", "ट्रैकर"),
            (350, "Planner", "📋", "प्लानर"),
            (500, "Pro", "⭐", "प्रो"),
            (750, "Expert", "🏆", "विशेषज्ञ"),
            (1000, "Master", "👑", "मास्टर"),
        ]
        
        current_level = levels[0]
        next_level = levels[1] if len(levels) > 1 else None
        
        for i, (threshold, name, icon, name_hi) in enumerate(levels):
            if points >= threshold:
                current_level = (threshold, name, icon, name_hi)
                next_level = levels[i + 1] if i + 1 < len(levels) else None
        
        progress = 0
        points_needed = 0
        if next_level:
            level_range = next_level[0] - current_level[0]
            progress_in_level = points - current_level[0]
            progress = int(progress_in_level / level_range * 100)
            points_needed = next_level[0] - points
        
        return {
            "level": current_level[1],
            "level_hi": current_level[3],
            "icon": current_level[2],
            "points": points,
            "next_level": next_level[1] if next_level else None,
            "progress": progress,
            "points_to_next": points_needed
        }
    
    def get_random_tip(self, language: str = "en") -> str:
        """Get random financial tip"""
        tips = self.tips.get(language, self.tips["en"])
        return random.choice(tips)
    
    def get_motivational_message(self, user_id: str, language: str = "en") -> str:
        """Get personalized motivational message"""
        
        user = user_repo.get_user(user_id)
        if not user:
            return ""
        
        streak = user.get("streak_days", 0)
        name = user.get("name", "Friend")
        
        messages = {
            "en": [
                f"💪 {name}, you're doing great!",
                f"🌟 Keep tracking, {name}! Every rupee counts.",
                f"🎯 {name}, small steps lead to big savings!",
                f"🔥 {streak} day streak! You're on fire!",
                f"💰 {name}, your future self will thank you!",
                f"📈 Progress, not perfection. Keep going!",
            ],
            "hi": [
                f"💪 {name}, बहुत अच्छा कर रहे हो!",
                f"🌟 ट्रैक करते रहो, {name}! हर रुपया मायने रखता है।",
                f"🎯 {name}, छोटे कदम बड़ी बचत की ओर ले जाते हैं!",
                f"🔥 {streak} दिन का स्ट्रीक! जबरदस्त!",
                f"💰 {name}, भविष्य का तुम धन्यवाद देगा!",
                f"📈 परफेक्ट नहीं, प्रोग्रेस। आगे बढ़ते रहो!",
            ]
        }
        
        msg_list = messages.get(language, messages["en"])
        return random.choice(msg_list)


class SmartInsightsService:
    """AI-powered insights and predictions"""
    
    def __init__(self):
        pass
    
    def get_spending_insights(self, user_id: str) -> List[Dict]:
        """Generate smart spending insights"""
        
        insights = []
        patterns = transaction_repo.get_spending_patterns(user_id)
        
        # Unusual spending detection
        for warning in patterns.get("warnings", []):
            insights.append({
                "type": "warning",
                "icon": "⚠️",
                "title": "Unusual Spending",
                "message": warning
            })
        
        # Category analysis
        current = patterns.get("current_month", {})
        last = patterns.get("last_month", {})
        
        # Find biggest expense category
        if current:
            biggest = max(current.items(), key=lambda x: x[1])
            if biggest[1] > 0:
                insights.append({
                    "type": "info",
                    "icon": "📊",
                    "title": "Top Expense",
                    "message": f"{biggest[0].title()} is your biggest expense (₹{biggest[1]:,})"
                })
        
        # Improvement opportunities
        for cat in ["entertainment", "shopping", "food"]:
            if cat in current and current[cat] > 0:
                if cat in last and current[cat] > last[cat] * 1.3:
                    insights.append({
                        "type": "tip",
                        "icon": "💡",
                        "title": f"Reduce {cat.title()}",
                        "message": f"Your {cat} spending increased 30%+. Consider cutting back."
                    })
        
        return insights
    
    def predict_month_end_balance(self, user_id: str) -> Dict:
        """Predict month-end balance based on current trends"""
        
        today = datetime.now()
        day_of_month = today.day
        days_in_month = 30  # Approximation
        
        # Get current month data
        summary = transaction_repo.get_monthly_summary(user_id)
        current_income = summary.get("total_income", 0)
        current_expense = summary.get("total_expense", 0)
        
        # Project to end of month
        if day_of_month > 0:
            projected_income = (current_income / day_of_month) * days_in_month
            projected_expense = (current_expense / day_of_month) * days_in_month
        else:
            projected_income = 0
            projected_expense = 0
        
        projected_savings = projected_income - projected_expense
        
        return {
            "current_day": day_of_month,
            "days_remaining": days_in_month - day_of_month,
            "current_income": current_income,
            "current_expense": current_expense,
            "projected_income": int(projected_income),
            "projected_expense": int(projected_expense),
            "projected_savings": int(projected_savings),
            "on_track": projected_savings > 0
        }
    
    def get_saving_opportunity(self, user_id: str) -> Optional[Dict]:
        """Find specific saving opportunities"""
        
        expenses = transaction_repo.get_expense_by_category(user_id)
        
        # Check each category for reduction potential
        reduction_targets = {
            "entertainment": 0.3,  # Can reduce by 30%
            "shopping": 0.25,
            "food": 0.15,
            "transport": 0.10
        }
        
        for cat, reduction in reduction_targets.items():
            if cat in expenses and expenses[cat] > 1000:
                potential = int(expenses[cat] * reduction)
                if potential >= 500:
                    return {
                        "category": cat,
                        "current_spending": expenses[cat],
                        "potential_savings": potential,
                        "suggestion": f"Reduce {cat} by {int(reduction*100)}% to save ₹{potential:,}/month"
                    }
        
        return None


class SmartReplyService:
    """Generate smart, contextual replies with voice"""
    
    def __init__(self):
        self.gamification = GamificationService()
        self.insights = SmartInsightsService()
    
    def enhance_reply(self, user_id: str, base_reply: str, language: str = "en") -> Dict:
        """Enhance reply with gamification, tips, and voice"""
        
        enhanced = base_reply
        
        # Check for new achievements
        new_achievements = self.gamification.check_achievements(user_id)
        for ach in new_achievements:
            enhanced += self.gamification.get_achievement_message(ach, language)
        
        # Add random tip (20% chance)
        if random.random() < 0.2:
            tip = self.gamification.get_random_tip(language)
            enhanced += f"\n\n{tip}"
        
        # Add motivational message on income entry (30% chance)
        if "income" in base_reply.lower() or "आमदनी" in base_reply or "வருமானம்" in base_reply:
            if random.random() < 0.3:
                motivation = self.gamification.get_motivational_message(user_id, language)
                enhanced += f"\n\n{motivation}"
        
        # Generate voice text (cleaner version without emojis)
        voice_text = self._text_to_voice_text(enhanced)
        
        # Generate voice file
        from services.voice_service import voice_service
        voice_path = voice_service.generate_voice(voice_text, language)
        
        return {
            "text": enhanced,
            "voice_text": voice_text,
            "voice_path": voice_path,
            "achievements": new_achievements
        }
    
    def _text_to_voice_text(self, text: str) -> str:
        """Convert text to voice-friendly version"""
        import re
        
        # Remove emojis
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"
            u"\U0001F300-\U0001F5FF"
            u"\U0001F680-\U0001F6FF"
            u"\U0001F1E0-\U0001F1FF"
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            u"\U0001f926-\U0001f937"
            u"\U00010000-\U0010ffff"
            "]+", flags=re.UNICODE)
        
        clean = emoji_pattern.sub('', text)
        
        # Remove markdown
        clean = re.sub(r'\*+', '', clean)
        clean = re.sub(r'_+', '', clean)
        clean = re.sub(r'[═╔╗║╚╝╠╣━]+', '', clean)
        clean = re.sub(r'\[.*?\]', '', clean)
        clean = re.sub(r'[░▓█▀▄]+', '', clean)
        
        # Clean up extra whitespace
        clean = re.sub(r'\n+', '. ', clean)
        clean = re.sub(r'\s+', ' ', clean)
        
        return clean.strip()


# Global instances
gamification_service = GamificationService()
smart_insights = SmartInsightsService()
smart_reply_service = SmartReplyService()
