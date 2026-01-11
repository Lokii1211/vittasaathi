"""
Dashboard Service - Monthly visual dashboard and analytics
"""
from datetime import datetime, timedelta
from typing import Dict, List
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from database.transaction_repository import transaction_repo
from database.user_repository import user_repo
from database.goal_repository import goal_repo
from database.budget_repository import budget_repo


class DashboardService:
    """Generate beautiful text-based dashboards for WhatsApp"""
    
    def __init__(self):
        pass
    
    def generate_monthly_dashboard(self, user_id: str, month: str = None) -> Dict:
        """Generate comprehensive monthly dashboard"""
        
        user = user_repo.get_user(user_id)
        if not user:
            return {"error": "User not found"}
        
        name = user.get("name", "Friend")
        language = user.get("language", "en")
        
        # Get current and last month
        if not month:
            month = datetime.now().strftime("%Y-%m")
        
        current_date = datetime.strptime(month + "-01", "%Y-%m-%d")
        last_month = (current_date.replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
        
        # Get summaries
        current = transaction_repo.get_monthly_summary(user_id, month)
        previous = transaction_repo.get_monthly_summary(user_id, last_month)
        
        # Calculate changes
        changes = self._calculate_changes(current, previous)
        
        # Get goal progress
        goals = goal_repo.get_goal_summary(user_id)
        
        # Build dashboard
        dashboard = self._build_dashboard_text(
            user_id, name, month, current, previous, changes, goals, language
        )
        
        # Build voice summary
        voice_text = self._build_voice_summary(
            name, current, changes, language
        )
        
        return {
            "dashboard": dashboard,
            "voice_text": voice_text,
            "data": {
                "current_month": current,
                "previous_month": previous,
                "changes": changes,
                "goals": goals
            }
        }
    
    def _calculate_changes(self, current: Dict, previous: Dict) -> Dict:
        """Calculate percentage changes"""
        
        def calc_change(curr, prev):
            if prev == 0:
                return 100 if curr > 0 else 0
            return round((curr - prev) / prev * 100, 1)
        
        return {
            "income_change": calc_change(
                current.get("total_income", 0),
                previous.get("total_income", 0)
            ),
            "expense_change": calc_change(
                current.get("total_expense", 0),
                previous.get("total_expense", 0)
            ),
            "savings_change": calc_change(
                current.get("net_savings", 0),
                previous.get("net_savings", 0)
            ),
            "income_trend": "📈" if current.get("total_income", 0) > previous.get("total_income", 0) else "📉" if current.get("total_income", 0) < previous.get("total_income", 0) else "➡️",
            "expense_trend": "📈" if current.get("total_expense", 0) > previous.get("total_expense", 0) else "📉" if current.get("total_expense", 0) < previous.get("total_expense", 0) else "➡️",
            "savings_trend": "📈" if current.get("net_savings", 0) > previous.get("net_savings", 0) else "📉" if current.get("net_savings", 0) < previous.get("net_savings", 0) else "➡️",
        }
    
    def _build_dashboard_text(
        self, user_id: str, name: str, month: str, current: Dict, previous: Dict, 
        changes: Dict, goals: Dict, language: str
    ) -> str:
        """Build beautiful text dashboard"""
        
        income = current.get("total_income", 0)
        expense = current.get("total_expense", 0)
        savings = current.get("net_savings", 0)
        savings_rate = current.get("savings_rate", 0)
        
        prev_income = previous.get("total_income", 0)
        prev_expense = previous.get("total_expense", 0)
        prev_savings = previous.get("net_savings", 0)
        
        # Progress bars
        income_bar = self._make_progress_bar(income, max(income, prev_income) * 1.2 if prev_income else income * 1.2)
        expense_bar = self._make_progress_bar(expense, max(expense, prev_expense) * 1.2 if prev_expense else expense * 1.2)
        savings_bar = self._make_progress_bar(max(0, savings), income if income > 0 else 1)
        
        # Top expenses
        top_expenses = current.get("expense_by_category", {})
        sorted_expenses = sorted(top_expenses.items(), key=lambda x: x[1], reverse=True)[:5]
        
        if language == "hi":
            month_name = self._get_month_name_hi(month)
            dashboard = f"""
╔══════════════════════════════════╗
║  📊 *{name} का मासिक डैशबोर्ड*  ║
║        {month_name}        ║
╠══════════════════════════════════╣

💰 *आय (Income)*
{income_bar}
₹{income:,} {changes['income_trend']} {'+' if changes['income_change'] >= 0 else ''}{changes['income_change']}%

💸 *खर्च (Expenses)*  
{expense_bar}
₹{expense:,} {changes['expense_trend']} {'+' if changes['expense_change'] >= 0 else ''}{changes['expense_change']}%

💾 *बचत (Savings)*
{savings_bar}
₹{savings:,} ({savings_rate}%) {changes['savings_trend']}

═══════════════════════════════════

📊 *खर्च विश्लेषण:*
"""
            for cat, amt in sorted_expenses:
                pct = round(amt / expense * 100, 1) if expense > 0 else 0
                bar = self._make_mini_bar(pct)
                dashboard += f"  {self._get_category_emoji(cat)} {cat}: ₹{amt:,} {bar} {pct}%\n"
            
            # Goals
            if goals.get("active_goals", 0) > 0:
                dashboard += f"""
═══════════════════════════════════

🎯 *गोल प्रगति:*
"""
                for g in goals.get("goals", [])[:3]:
                    if g["status"] == "active":
                        goal_bar = self._make_progress_bar(g["saved_amount"], g["target_amount"])
                        dashboard += f"  {g['icon']} {g['name']}\n  {goal_bar} {g['progress_percent']}%\n"
            
            # Health score
            from services.financial_advisor import financial_advisor
            health = financial_advisor.get_financial_health_score(user_id)
            
            dashboard += f"""
═══════════════════════════════════

🏥 *फाइनेंशियल हेल्थ: {health['health']['grade']}*
{self._make_health_bar(health['total_score'])} {health['total_score']}/100

╚══════════════════════════════════╝
"""
        else:  # English default
            month_name = datetime.strptime(month + "-01", "%Y-%m-%d").strftime("%B %Y")
            dashboard = f"""
╔══════════════════════════════════╗
║  📊 *{name}'s Monthly Dashboard*  ║
║        {month_name}        ║
╠══════════════════════════════════╣

💰 *Income*
{income_bar}
₹{income:,} {changes['income_trend']} {'+' if changes['income_change'] >= 0 else ''}{changes['income_change']}% vs last month

💸 *Expenses*
{expense_bar}
₹{expense:,} {changes['expense_trend']} {'+' if changes['expense_change'] >= 0 else ''}{changes['expense_change']}% vs last month

💾 *Savings*
{savings_bar}
₹{savings:,} ({savings_rate}% of income) {changes['savings_trend']}

═══════════════════════════════════

📊 *Expense Breakdown:*
"""
            for cat, amt in sorted_expenses:
                pct = round(amt / expense * 100, 1) if expense > 0 else 0
                bar = self._make_mini_bar(pct)
                dashboard += f"  {self._get_category_emoji(cat)} {cat.title()}: ₹{amt:,} {bar} {pct}%\n"
            
            # Goals
            if goals.get("active_goals", 0) > 0:
                dashboard += f"""
═══════════════════════════════════

🎯 *Goal Progress:*
"""
                for g in goals.get("goals", [])[:3]:
                    if g["status"] == "active":
                        goal_bar = self._make_progress_bar(g["saved_amount"], g["target_amount"])
                        dashboard += f"  {g['icon']} {g['name']}\n  {goal_bar} {g['progress_percent']}%\n"
            
            # Health score
            from services.financial_advisor import financial_advisor
            health = financial_advisor.get_financial_health_score(user_id)
            
            dashboard += f"""
═══════════════════════════════════

🏥 *Financial Health: {health['health']['grade']}*
{self._make_health_bar(health['total_score'])} {health['total_score']}/100

╚══════════════════════════════════╝
"""
        
        return dashboard
    
    def _build_voice_summary(self, name: str, current: Dict, changes: Dict, language: str) -> str:
        """Build voice-friendly summary"""
        
        income = current.get("total_income", 0)
        expense = current.get("total_expense", 0)
        savings = current.get("net_savings", 0)
        
        if language == "hi":
            text = f"{name}, इस महीने आपने {income} रुपये कमाए और {expense} रुपये खर्च किए। "
            text += f"आपकी बचत {savings} रुपये है। "
            
            if changes["income_change"] > 0:
                text += f"पिछले महीने के मुकाबले आय {abs(changes['income_change'])} प्रतिशत बढ़ी है। "
            elif changes["income_change"] < 0:
                text += f"पिछले महीने के मुकाबले आय {abs(changes['income_change'])} प्रतिशत कम हुई है। "
            
            if savings > 0:
                text += "शाबाश! बचत जारी रखें।"
            else:
                text += "अगले महीने खर्च कम करने की कोशिश करें।"
        
        elif language == "ta":
            text = f"{name}, இந்த மாதம் நீங்கள் {income} ரூபாய் சம்பாதித்தீர்கள், {expense} ரூபாய் செலவழித்தீர்கள். "
            text += f"உங்கள் சேமிப்பு {savings} ரூபாய். "
        
        elif language == "te":
            text = f"{name}, ఈ నెల మీరు {income} రూపాయలు సంపాదించారు, {expense} రూపాయలు ఖర్చు చేశారు. "
            text += f"మీ పొదుపు {savings} రూపాయలు. "
        
        else:  # English
            text = f"{name}, this month you earned {income} rupees and spent {expense} rupees. "
            text += f"Your savings are {savings} rupees. "
            
            if changes["income_change"] > 0:
                text += f"Your income increased by {abs(changes['income_change'])} percent compared to last month. "
            elif changes["income_change"] < 0:
                text += f"Your income decreased by {abs(changes['income_change'])} percent compared to last month. "
            
            if savings > 0:
                text += "Great job! Keep saving."
            else:
                text += "Try to reduce expenses next month."
        
        return text
    
    def _make_progress_bar(self, value: float, max_value: float, length: int = 20) -> str:
        """Create text progress bar"""
        if max_value <= 0:
            return "░" * length
        
        filled = int((value / max_value) * length)
        filled = min(filled, length)
        
        bar = "█" * filled + "░" * (length - filled)
        return f"[{bar}]"
    
    def _make_mini_bar(self, percentage: float, length: int = 10) -> str:
        """Create mini progress bar"""
        filled = int(percentage / 10)
        filled = min(filled, length)
        return "▓" * filled + "░" * (length - filled)
    
    def _make_health_bar(self, score: int) -> str:
        """Create health score bar with color indicators"""
        if score >= 80:
            return "🟢🟢🟢🟢🟢"
        elif score >= 60:
            return "🟢🟢🟢🟢⚪"
        elif score >= 40:
            return "🟡🟡🟡⚪⚪"
        elif score >= 20:
            return "🟠🟠⚪⚪⚪"
        else:
            return "🔴⚪⚪⚪⚪"
    
    def _get_category_emoji(self, category: str) -> str:
        """Get emoji for expense category"""
        emojis = {
            "food": "🍔", "transport": "🚗", "petrol": "⛽", "rent": "🏠",
            "utilities": "💡", "healthcare": "💊", "education": "📚",
            "entertainment": "🎬", "shopping": "🛍️", "mobile_recharge": "📱",
            "family": "👨‍👩‍👧", "savings": "💰", "investment": "📈",
            "other_expense": "📦", "other_income": "💵"
        }
        return emojis.get(category, "📦")
    
    def _get_month_name_hi(self, month: str) -> str:
        """Get Hindi month name"""
        months = {
            "01": "जनवरी", "02": "फरवरी", "03": "मार्च", "04": "अप्रैल",
            "05": "मई", "06": "जून", "07": "जुलाई", "08": "अगस्त",
            "09": "सितंबर", "10": "अक्टूबर", "11": "नवंबर", "12": "दिसंबर"
        }
        year, m = month.split("-")
        return f"{months.get(m, m)} {year}"
    
    def generate_weekly_dashboard(self, user_id: str) -> Dict:
        """Generate weekly mini-dashboard"""
        
        user = user_repo.get_user(user_id)
        if not user:
            return {"error": "User not found"}
        
        name = user.get("name", "Friend")
        language = user.get("language", "en")
        
        # Get last 7 days
        today = datetime.now()
        week_start = today - timedelta(days=7)
        
        txns = transaction_repo.get_user_transactions(
            user_id,
            start_date=week_start,
            end_date=today,
            limit=100
        )
        
        income = sum(t["amount"] for t in txns if t["type"] == "income")
        expense = sum(t["amount"] for t in txns if t["type"] == "expense")
        
        # Daily averages
        daily_income = income / 7
        daily_expense = expense / 7
        
        if language == "hi":
            dashboard = f"""
📊 *साप्ताहिक रिपोर्ट*
━━━━━━━━━━━━━━━━━━━

💰 कुल आय: ₹{income:,}
   (औसत ₹{int(daily_income):,}/दिन)

💸 कुल खर्च: ₹{expense:,}
   (औसत ₹{int(daily_expense):,}/दिन)

📈 नेट: ₹{income - expense:,}
━━━━━━━━━━━━━━━━━━━
"""
        else:
            dashboard = f"""
📊 *Weekly Report*
━━━━━━━━━━━━━━━━━━━

💰 Total Income: ₹{income:,}
   (Avg ₹{int(daily_income):,}/day)

💸 Total Expenses: ₹{expense:,}
   (Avg ₹{int(daily_expense):,}/day)

📈 Net: ₹{income - expense:,}
━━━━━━━━━━━━━━━━━━━
"""
        
        voice = f"Weekly summary: You earned {income} rupees and spent {expense} rupees. Net savings {income - expense} rupees."
        
        return {"dashboard": dashboard, "voice_text": voice}


# Global instance
dashboard_service = DashboardService()

