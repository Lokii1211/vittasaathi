"""
Financial Calendar Service
==========================
Track income/expense patterns, predict earning days, manage events
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from collections import defaultdict
import calendar
import sys

sys.path.append(str(Path(__file__).parent.parent))

from database.user_repository import user_repo
from database.transaction_repository import transaction_repo
from config import EXPENSE_CATEGORIES, INCOME_CATEGORIES


class FinancialCalendarService:
    """Financial calendar with patterns and predictions"""
    
    def __init__(self):
        self.special_dates = self._load_special_dates()
    
    def _load_special_dates(self) -> Dict[str, List[Dict]]:
        """Load special financial dates (Indian context)"""
        return {
            "recurring": [
                {"day": 1, "name": "Rent Due", "icon": "🏠", "type": "expense"},
                {"day": 5, "name": "Credit Card Due (typical)", "icon": "💳", "type": "expense"},
                {"day": 7, "name": "Salary Week (typical)", "icon": "💰", "type": "income"},
                {"day": 10, "name": "LPG Subsidy", "icon": "🔥", "type": "income"},
                {"day": 15, "name": "Mid-month Review", "icon": "📊", "type": "review"},
                {"day": 28, "name": "Month-end Bonus", "icon": "🎯", "type": "income"},
            ],
            "2026": {
                "01-14": {"name": "Makar Sankranti", "icon": "🪁", "type": "festival", "tip": "Festival spending expected"},
                "01-26": {"name": "Republic Day", "icon": "🇮🇳", "type": "holiday", "tip": "Possible bonus/holiday pay"},
                "03-14": {"name": "Holi", "icon": "🎨", "type": "festival", "tip": "Budget for celebrations"},
                "04-14": {"name": "Baisakhi", "icon": "🌾", "type": "festival", "tip": "Harvest bonus possible"},
                "08-15": {"name": "Independence Day", "icon": "🇮🇳", "type": "holiday", "tip": "Possible bonus"},
                "10-02": {"name": "Gandhi Jayanti", "icon": "🕊️", "type": "holiday", "tip": "Bank holiday"},
                "10-20": {"name": "Dussehra (approx)", "icon": "🏹", "type": "festival", "tip": "Major spending expected"},
                "11-10": {"name": "Diwali (approx)", "icon": "🪔", "type": "festival", "tip": "Biggest spending month, plan ahead!"},
                "12-25": {"name": "Christmas", "icon": "🎄", "type": "festival", "tip": "Year-end bonuses possible"},
            }
        }
    
    def get_month_calendar(self, user_id: str, year: int = None, month: int = None) -> Dict:
        """Get financial calendar for a month"""
        
        today = datetime.now()
        year = year or today.year
        month = month or today.month
        
        # Get month info
        first_day, num_days = calendar.monthrange(year, month)
        month_name = datetime(year, month, 1).strftime("%B %Y")
        
        # Initialize calendar data
        cal_data = {
            "year": year,
            "month": month,
            "month_name": month_name,
            "first_weekday": first_day,  # 0=Monday
            "num_days": num_days,
            "days": []
        }
        
        # Get user's transaction history for pattern detection
        patterns = self._analyze_patterns(user_id)
        
        # Build each day
        for day in range(1, num_days + 1):
            date_str = f"{year}-{month:02d}-{day:02d}"
            date_obj = datetime(year, month, day)
            
            day_data = {
                "day": day,
                "date": date_str,
                "weekday": date_obj.strftime("%a"),
                "is_today": date_obj.date() == today.date(),
                "is_past": date_obj.date() < today.date(),
                "events": [],
                "predicted_income": 0,
                "predicted_expense": 0,
                "actual_income": 0,
                "actual_expense": 0
            }
            
            # Add actual transactions for past/today
            if day_data["is_past"] or day_data["is_today"]:
                summary = transaction_repo.get_daily_summary(user_id, date_str)
                day_data["actual_income"] = summary.get("income", 0)
                day_data["actual_expense"] = summary.get("expense", 0)
            
            # Add predictions for future
            if not day_data["is_past"]:
                day_data["predicted_income"] = self._predict_day_income(patterns, date_obj)
                day_data["predicted_expense"] = self._predict_day_expense(patterns, date_obj, day)
            
            # Add recurring events
            for event in self.special_dates["recurring"]:
                if event["day"] == day:
                    day_data["events"].append(event)
            
            # Add special dates
            year_dates = self.special_dates.get(str(year), {})
            date_key = f"{month:02d}-{day:02d}"
            if date_key in year_dates:
                day_data["events"].append(year_dates[date_key])
            
            # Add user's bill reminders
            user = user_repo.get_user(user_id)
            if user:
                for bill in user.get("bill_reminders", []):
                    if bill.get("due_date") == day:
                        day_data["events"].append({
                            "name": f"{bill['type'].title()} Bill Due",
                            "icon": "📄",
                            "type": "bill",
                            "amount": bill.get("amount", 0)
                        })
            
            # Identify high earning/spending days from patterns
            weekday = date_obj.weekday()
            if weekday in patterns.get("high_earning_days", []):
                day_data["events"].append({
                    "name": "Typically High Earning Day",
                    "icon": "📈",
                    "type": "pattern"
                })
            
            cal_data["days"].append(day_data)
        
        # Add month summary
        cal_data["summary"] = self._get_month_summary(user_id, year, month)
        
        return cal_data
    
    def _analyze_patterns(self, user_id: str) -> Dict:
        """Analyze user's transaction patterns"""
        
        patterns = {
            "high_earning_days": [],
            "high_spending_days": [],
            "avg_daily_income": 0,
            "avg_daily_expense": 0,
            "weekend_vs_weekday": {}
        }
        
        # Get last 60 days of transactions
        by_weekday_income = defaultdict(list)
        by_weekday_expense = defaultdict(list)
        
        today = datetime.now()
        
        for i in range(60):
            date = today - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            summary = transaction_repo.get_daily_summary(user_id, date_str)
            
            weekday = date.weekday()
            by_weekday_income[weekday].append(summary.get("income", 0))
            by_weekday_expense[weekday].append(summary.get("expense", 0))
        
        # Find average per weekday
        avg_income_by_day = {}
        avg_expense_by_day = {}
        
        for day in range(7):
            if by_weekday_income[day]:
                avg_income_by_day[day] = sum(by_weekday_income[day]) / len(by_weekday_income[day])
            if by_weekday_expense[day]:
                avg_expense_by_day[day] = sum(by_weekday_expense[day]) / len(by_weekday_expense[day])
        
        # Find high earning days
        if avg_income_by_day:
            overall_avg = sum(avg_income_by_day.values()) / len(avg_income_by_day)
            patterns["avg_daily_income"] = overall_avg
            patterns["high_earning_days"] = [
                day for day, avg in avg_income_by_day.items() 
                if avg > overall_avg * 1.2
            ]
        
        # Find high spending days
        if avg_expense_by_day:
            overall_avg = sum(avg_expense_by_day.values()) / len(avg_expense_by_day)
            patterns["avg_daily_expense"] = overall_avg
            patterns["high_spending_days"] = [
                day for day, avg in avg_expense_by_day.items()
                if avg > overall_avg * 1.3
            ]
        
        # Weekend vs weekday
        weekend_income = (avg_income_by_day.get(5, 0) + avg_income_by_day.get(6, 0)) / 2
        weekday_income = sum(avg_income_by_day.get(d, 0) for d in range(5)) / 5
        
        patterns["weekend_vs_weekday"] = {
            "weekend_income": weekend_income,
            "weekday_income": weekday_income,
            "better_for_income": "weekend" if weekend_income > weekday_income else "weekday"
        }
        
        return patterns
    
    def _predict_day_income(self, patterns: Dict, date: datetime) -> int:
        """Predict income for a future day"""
        
        weekday = date.weekday()
        base = patterns.get("avg_daily_income", 500)
        
        # Weekend adjustment
        if weekday >= 5:
            if patterns.get("weekend_vs_weekday", {}).get("better_for_income") == "weekend":
                base *= 1.2
            else:
                base *= 0.8
        
        # High earning day adjustment
        if weekday in patterns.get("high_earning_days", []):
            base *= 1.3
        
        return int(base)
    
    def _predict_day_expense(self, patterns: Dict, date: datetime, day: int) -> int:
        """Predict expense for a future day"""
        
        base = patterns.get("avg_daily_expense", 400)
        
        # Weekend = more spending
        if date.weekday() >= 5:
            base *= 1.4
        
        # Start of month = high spending (rent, etc)
        if day <= 5:
            base *= 1.5
        
        # End of month = tighter budget
        if day >= 25:
            base *= 0.8
        
        return int(base)
    
    def _get_month_summary(self, user_id: str, year: int, month: int) -> Dict:
        """Get summary for calendar month"""
        
        month_str = f"{year}-{month:02d}"
        summary = transaction_repo.get_monthly_summary(user_id, month_str)
        
        return {
            "total_income": summary.get("total_income", 0),
            "total_expense": summary.get("total_expense", 0),
            "net": summary.get("net_savings", 0),
            "transaction_count": summary.get("transaction_count", 0)
        }
    
    def get_upcoming_events(self, user_id: str, days: int = 14) -> List[Dict]:
        """Get upcoming financial events"""
        
        events = []
        today = datetime.now()
        
        # Get user bills
        user = user_repo.get_user(user_id)
        bills = user.get("bill_reminders", []) if user else []
        
        for i in range(days):
            date = today + timedelta(days=i)
            day = date.day
            date_str = date.strftime("%Y-%m-%d")
            
            # Bill reminders
            for bill in bills:
                if bill.get("due_date") == day:
                    events.append({
                        "date": date_str,
                        "days_from_now": i,
                        "name": f"{bill['type'].title()} Bill",
                        "icon": "📄",
                        "type": "bill",
                        "amount": bill.get("amount", 0),
                        "priority": "high" if i <= 3 else "medium"
                    })
            
            # Recurring events
            for event in self.special_dates["recurring"]:
                if event["day"] == day:
                    events.append({
                        "date": date_str,
                        "days_from_now": i,
                        **event,
                        "priority": "low"
                    })
            
            # Special dates
            year_dates = self.special_dates.get(str(date.year), {})
            date_key = f"{date.month:02d}-{day:02d}"
            if date_key in year_dates:
                event = year_dates[date_key]
                events.append({
                    "date": date_str,
                    "days_from_now": i,
                    **event,
                    "priority": "medium"
                })
        
        # Sort by date
        events.sort(key=lambda x: x["days_from_now"])
        
        return events
    
    def get_text_calendar(self, user_id: str, year: int = None, month: int = None) -> str:
        """Generate text-based calendar for WhatsApp"""
        
        cal_data = self.get_month_calendar(user_id, year, month)
        
        # Header
        calendar_text = f"""
📅 *{cal_data['month_name']}*
━━━━━━━━━━━━━━━━━━━━━
Mon  Tue  Wed  Thu  Fri  Sat  Sun
"""
        
        # Build weeks
        days = cal_data["days"]
        first_weekday = cal_data["first_weekday"]
        
        # Padding for first week
        week_line = "     " * first_weekday
        
        for i, day_data in enumerate(days):
            actual_weekday = (first_weekday + i) % 7
            
            # Format day with indicator
            day_num = day_data["day"]
            
            if day_data["is_today"]:
                day_str = f"[{day_num:2d}]"
            elif day_data["events"]:
                day_str = f"*{day_num:2d}*"
            else:
                day_str = f" {day_num:2d} "
            
            week_line += day_str + " "
            
            # New line after Sunday
            if actual_weekday == 6:
                calendar_text += week_line + "\n"
                week_line = ""
        
        # Last incomplete week
        if week_line:
            calendar_text += week_line + "\n"
        
        # Add summary
        summary = cal_data["summary"]
        calendar_text += f"""
━━━━━━━━━━━━━━━━━━━━━
💰 Income: ₹{summary['total_income']:,}
💸 Expense: ₹{summary['total_expense']:,}
💾 Saved: ₹{summary['net']:,}

🔑 [X] = Today | *X* = Has event
"""
        
        # Add upcoming events
        upcoming = self.get_upcoming_events(user_id, 7)
        if upcoming:
            calendar_text += "\n📋 *Upcoming:*\n"
            for event in upcoming[:5]:
                calendar_text += f"{event['icon']} {event['name']}"
                if event.get('amount'):
                    calendar_text += f" (₹{event['amount']:,})"
                if event['days_from_now'] == 0:
                    calendar_text += " - TODAY!"
                elif event['days_from_now'] == 1:
                    calendar_text += " - Tomorrow"
                else:
                    calendar_text += f" - in {event['days_from_now']} days"
                calendar_text += "\n"
        
        return calendar_text
    
    def get_earning_forecast(self, user_id: str, days: int = 30) -> Dict:
        """Forecast earnings for upcoming days"""
        
        patterns = self._analyze_patterns(user_id)
        today = datetime.now()
        
        forecast = []
        total_predicted_income = 0
        total_predicted_expense = 0
        
        for i in range(days):
            date = today + timedelta(days=i)
            
            income = self._predict_day_income(patterns, date)
            expense = self._predict_day_expense(patterns, date, date.day)
            
            forecast.append({
                "date": date.strftime("%Y-%m-%d"),
                "day_name": date.strftime("%a"),
                "predicted_income": income,
                "predicted_expense": expense,
                "predicted_net": income - expense
            })
            
            total_predicted_income += income
            total_predicted_expense += expense
        
        return {
            "forecast": forecast,
            "total_predicted_income": total_predicted_income,
            "total_predicted_expense": total_predicted_expense,
            "predicted_net": total_predicted_income - total_predicted_expense,
            "patterns": {
                "high_earning_days": [
                    calendar.day_name[d] for d in patterns.get("high_earning_days", [])
                ],
                "high_spending_days": [
                    calendar.day_name[d] for d in patterns.get("high_spending_days", [])
                ],
                "better_income_on": patterns.get("weekend_vs_weekday", {}).get("better_for_income", "weekday")
            }
        }


# Global instance
calendar_service = FinancialCalendarService()
